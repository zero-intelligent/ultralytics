import gc
import random
import time
import cv2
from ultralytics import YOLO
import mcd.conf as conf
from mcd.logger import log
from mcd.custom_result import PersonResults
from mcd.event import config_changed_event


def get_current_person_detect_result():
    return {id:int(v['time_s']) for id,v in PersonResults.id_info.items()}

def get_person_detect_result(detect_result):
    detect_result.__class__ = PersonResults
    tracked_frame = detect_result.plot()  # 获取带检测结果的帧
    return array2jpg(tracked_frame)

def person_detect_frames():
    return detect_frames(get_person_detect_result)

state = {
    "running_state": "ready", #运行状态：准备（ready), 装载中(loading), 运行中(running), 结束（finished)
    "frame_count": 0,
    "frame_rate": 0
}


def change_running_state(new_state):
    if state['running_state'] != new_state:
        state['running_state'] = new_state
        config_changed_event.set() # 通知状态变更
        
def swith_mode(mode:str):
    if mode not in ('huiji_detect','person_detect'):
        raise Exception(f"只支持 'huiji_detect','person_detect'")
    if conf.current_mode == mode:
        return False
    if mode == 'person_detect':
        PersonResults.id_info = {}
    
    conf.current_mode = mode
    while state['running_state'] != 'finished':
        log.info(f"wait to last mode to finish.current:{state['running_state']}")
        time.sleep(0.3)
    change_running_state('ready')
    return True
        
    
def detect_frames(detect_results2trackedframe):
    # 初始化计算帧率配置
    start_time = time.time()
    state['frame_count'] = 0
    state['frame_rate'] = 0
    
    change_running_state('loading')
    
    model = YOLO(conf.current_detect_config()['model'])
    source = conf.data_source()
    mode = conf.current_mode
    classes = [0] if mode == 'person_detect' else None
    for result in model.track(source=source, stream=True,verbose=False,classes=classes):
        change_running_state('running')
        
        # 如果用户已经切换了mode或者数据源，当前的检测程序退出
        if conf.current_mode != mode or conf.data_source() != source:
            log.info(f"{conf.current_mode},data_source:{source} quiting")
            break
        
        #计算帧率
        state['frame_count'] += 1
        state['frame_rate'] = state['frame_count'] / (time.time() - start_time)
        
        if random.random() < conf.drop_rate:  # 按照一定的比率丢侦
            continue  # 跳过这一帧
        
        orig_frame = array2jpg(result.orig_img)  # 获取原始帧
        if not orig_frame:
            continue

        # 使用生成器同时返回两个流
        yield {
            "orig_frame": orig_frame,
            "tracked_frame": detect_results2trackedframe(result)
        }
    
    # 模型运行结束后，回收较重的模型资源
    del model
    gc.collect()
    change_running_state('finished')
    
def huiji_detect_frames():
    return detect_frames(huiji_detect_results)
        
def get_huiji_detect_items(detect_result):
    if not detect_result:
        detect_result = {}
    taocan_id = conf.huiji_detect_config['current_taocan_id']
    taocan =  [t for t in conf.huiji_detect_config['taocans'] if t['id'] == taocan_id]
    if not taocan:
        raise Exception(f"can't find taocao with id:{taocan_id}")
    taocan = taocan[0]
    
    in_tancan_results = [
        {
            'id': id,
            'name': next((f'{cn_name} {en_name}' for m_id,en_name,cn_name in conf.huiji_detect_config['meals_info'] if m_id == id),None),
            'count': count,
            'real_count': detect_result[id] if id in detect_result else 0,
            'lack_item': id not in detect_result,
            'lack_count': id in detect_result and  detect_result[id] < count,
            'is_in_taocan': True
        } for id,name,count in taocan['items']
    ]

    out_tancan_results = [
        {
            'id': id,
            'name': next((f'{cn_name} {en_name}' for m_id,en_name,cn_name in conf.huiji_detect_config['meals_info'] if m_id == id),None),
            'count': None,
            'real_count': count,
            'lack_item': None,
            'lack_count': None,
            'is_in_taocan': False
        } for id,count in detect_result.items() if id not in [i[0] for i in taocan['items']]
    ]
    has_incorrect = any([r['lack_item'] or r['lack_count'] for r in in_tancan_results]) or len(out_tancan_results) > 0
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


