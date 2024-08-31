from enum import Enum
import gc
import queue
import random
import threading
import time
import cv2
from mcd.util import profile
from ultralytics import YOLO
from mcd import conf
from mcd.logger import log
from mcd.custom_result import PersonResults
from mcd.event import config_changed_event
from mcd.domain_entities import DataSourceType, Mode, ModeDataSource, RunningState, TancanResult


def get_current_person_detect_result():
    return {id:int(v['time_s']) for id,v in PersonResults.id_info.items()}

def get_person_detect_result(detect_result):
    detect_result.__class__ = PersonResults
    tracked_frame = detect_result.plot()  # 获取带检测结果的帧
    return array2jpg(tracked_frame)


    
class VideoState:
    running_state:RunningState = RunningState.READY #运行状态：准备（ready), 装载中(loading), 运行中(running), 结束（finished)
    frame_count:int = 0
    frame_rate:int = 0
    detect_frame_exit:bool = False


def change_running_state(new_state):
    if VideoState.running_state != new_state:
        VideoState.running_state = new_state
        config_changed_event.set() # 通知状态变更
        
def swith_mode(mode:Mode):
    if conf.current_mode == mode:
        return False
    if mode == Mode.PERSON:
        PersonResults.id_info = {}
    
    conf.current_mode = mode
    # 通知正在运行的模型退出
    VideoState.detect_frame_exit = True
    
    change_running_state(RunningState.READY)
    
    while not video_frame_queue.empty():
        video_frame_queue.get()
    return True
        
def update_datasource(datasource:ModeDataSource):
    
    detect_config = conf.current_detect_config()
    
    #更新配置信息
    conf.current_mode = datasource.mode
    detect_config['data_source_type'] = datasource.data_source_type
    if datasource.data_source_type == DataSourceType.CAMERA:
        detect_config['camera_source'] = datasource.data_source
    else:
        detect_config['video_file'] = datasource.data_source
    
    # 通知正在运行的模型退出
    VideoState.detect_frame_exit = True
    
    change_running_state(RunningState.READY)
    while not video_frame_queue.empty():
        video_frame_queue.get()
    
    config_changed_event.set()

video_frame_queue = queue.Queue()

def run_detect_loop():
    def loop():
        while True:
            detect_frames()
    thread = threading.Thread(name="main_loop",target=loop,daemon=True)
    thread.start()

# @profile
def detect_frames():
    # 初始化计算帧率配置
    start_time = time.time()
    VideoState.frame_count = 0
    VideoState.frame_rate = 0
    
    change_running_state(RunningState.LOADING)
    
    model = YOLO(conf.current_detect_config()['model'])
    mode = conf.current_mode
    datasource_type = conf.current_detect_config()['data_source_type']
    source = conf.data_source()
    classes = [0] if mode == Mode.PERSON else None
    log.info(f"model:{conf.current_detect_config()['model']} is tracking source={source},stream=True,verbose=False,classes={source}")
    for result in model.track(source=source, stream=True,verbose=False,classes=classes):
        # 如果用户已经切换了mode或者数据源，当前的检测程序退出
        if (conf.current_mode,conf.current_detect_config()['data_source_type'], conf.data_source()) != (mode,datasource_type,source):
            log.info(f"{conf.current_mode},data_source:{source} quiting")
            break
        
         # 如果被标记退出，则退出
        if VideoState.detect_frame_exit:
            VideoState.detect_frame_exit = False
            break
        
        change_running_state(RunningState.RUNNING)

        #计算帧率
        VideoState.frame_count += 1
        VideoState.frame_rate = VideoState.frame_count / (time.time() - start_time)
        
        if random.random() < conf.drop_rate:  # 按照一定的比率丢侦
            continue  # 跳过这一帧
        
        orig_frame = array2jpg(result.orig_img)  # 获取原始帧
        if not orig_frame:
            continue

        if conf.current_mode == Mode.HUIJI:
            tracked_frame = huiji_detect_results(result)
        else:
            tracked_frame = get_person_detect_result(result)
            
        #将结果写入队列
        video_frame_queue.put({
            "orig_frame": orig_frame,
            "tracked_frame": tracked_frame
        })
    
    # 模型运行结束后，回收较重的模型资源
    del model
    gc.collect()
    change_running_state(RunningState.FINISHED)
    
        
def get_huiji_detect_items(detect_result):
    if not detect_result:
        detect_result = {}
    taocan_id = conf.huiji_detect_config['current_taocan_id']
    taocan =  [t for t in conf.huiji_detect_config['taocans'] if t['id'] == taocan_id]
    if not taocan:
        raise Exception(f"can't find taocao with id:{taocan_id}")
    taocan = taocan[0]
    
    in_tancan_results = [
        TancanResult(
            id = id,
            name = next((f'{cn_name} {en_name}' for m_id,en_name,cn_name in conf.huiji_detect_config['meals_info'] if m_id == id),None),
            count = count,
            real_count = detect_result[id] if id in detect_result else 0,
            lack_item = id not in detect_result,
            lack_count = id in detect_result and  detect_result[id] < count,
            is_in_taocan = True
        ) for id,name,count in taocan['items']
    ]

    out_tancan_results = [
        TancanResult(
            id = id,
            name = next((f'{cn_name} {en_name}' for m_id,en_name,cn_name in conf.huiji_detect_config['meals_info'] if m_id == id),None),
            count = None,
            real_count = count,
            lack_item = None,
            lack_count = None,
            is_in_taocan = False
        ) for id,count in detect_result.items() if id not in [i[0] for i in taocan['items']]
    ]
    has_incorrect = any([r.lack_item or r.lack_count for r in in_tancan_results]) or len(out_tancan_results) > 0
    result_state = 'incorrect' if has_incorrect else 'correct'
    results = in_tancan_results + out_tancan_results
    return result_state,results


last_taocan_check_result = None
current_taocan_check_result = None

def huiji_detect_results(results):
    img=None
    meal_result=None
    meal_result = {}
    for result in results:
        # 提取每个检测结果的 id 和 class 信息
        for obj in result.boxes:
            obj_id = obj.id.item() if hasattr(obj, 'id') and obj.id else 0
            obj_class = int(obj.cls.item())
            if obj_class not in meal_result:
                meal_result[obj_class]=set()
            meal_result[obj_class].add(obj_id)

    global current_taocan_check_result,last_taocan_check_result
    last_taocan_check_result = current_taocan_check_result
    current_taocan_check_result = {k:len(v) for k,v in meal_result.items()}
    if current_taocan_check_result != last_taocan_check_result:
        config_changed_event.set()
        
    # if current_taocan_check_result:
    #     log.info(f'huiji_detect camera source:{conf.huiji_detect_config['camera_source']} detect results:{current_taocan_check_result}')
    # else:
    #     pass
    img = results.plot()

    return array2jpg(img)


def capture_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(conf.data_source())
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # yield frame

    cap.release()
    

models = {}

def get_model(model_path):
    if not models.get(model_path):
        models[model_path] = YOLO(model_path)
    return models[model_path]

def array2jpg(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return None
    return buffer.tobytes()


def changed(detect_result):
    return detect_result != last_taocan_check_result


