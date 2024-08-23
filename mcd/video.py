import os
import time
import cv2
from ultralytics import YOLO
import mcd.conf as conf
from mcd.logger import log
from mcd.custom_result import PersonResults


def get_current_person_detect_result():
    return {id:v['time_s'] for id,v in PersonResults.id_info.items()}

person_detect_frame_rates = 0

def person_detect_frames():
    model = get_model(conf.person_detect_config['model'])
    
    # 开始时间
    start_time = time.time()
    frame_count = 0

    for result in model.track(source=data_source(), stream=True,verbose=False, classes=[0]):
        
        #计算帧率
        frame_count += 1
        global person_detect_frame_rates
        person_detect_frame_rates = frame_count / (time.time() - start_time)
        
        orig_frame = result.orig_img  # 获取原始帧
        # 编码原始帧为 JPEG
        ret, orig_buffer = cv2.imencode('.jpg', orig_frame)
        if not ret:
            continue
        orig_frame = orig_buffer.tobytes()
        
        result.__class__ = PersonResults
        tracked_frame = result.plot()  # 获取带检测结果的帧
        # 编码带检测结果的帧为 JPEG
        ret, tracked_buffer = cv2.imencode('.jpg', tracked_frame)
        if not ret:
            continue
        tracked_frame = tracked_buffer.tobytes()

        # 使用生成器同时返回两个流
        yield {
            "orig_frame": orig_frame,
            "tracked_frame": tracked_frame
        }

huiji_detect_frame_rates = 0

def huiji_detect_frames():
     # 开始时间
    start_time = time.time()
    frame_count = 0
    
    model = get_model(conf.huiji_detect_config['model'])
    for result in model.track(source=data_source(), stream=True,verbose=False):
        #计算帧率
        frame_count += 1
        global huiji_detect_frame_rates
        huiji_detect_frame_rates = frame_count / (time.time() - start_time)
        
        orig_frame = result.orig_img  # 获取原始帧

        # 编码原始帧为 JPEG
        ret, orig_buffer = cv2.imencode('.jpg', orig_frame)
        if not ret:
            continue
        orig_frame = orig_buffer.tobytes()

        # 使用生成器同时返回两个流
        yield {
            "orig_frame": orig_frame,
            "tracked_frame": huiji_detect_results(result)
        }
        
def get_huiji_detect_items(detect_result):
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
    return in_tancan_results + out_tancan_results


last_taocan_check_result = None
current_taocan_check_result = None

def huiji_detect_results(results):
    img=None
    meal_result=None
    meal_result = {}
    for result in results:
        # 提取每个检测结果的 id 和 class 信息
        for obj in result.boxes:
            obj_id = obj.id.item() if hasattr(obj, 'id') and obj.id else None
            if not obj_id:
                continue
            obj_class = int(obj.cls.item())
            if obj_class not in meal_result:
                meal_result[obj_class]=set()
            meal_result[obj_class].add(obj_id)

    global current_taocan_check_result,last_taocan_check_result
    last_taocan_check_result = current_taocan_check_result
    current_taocan_check_result = {k:len(v) for k,v in meal_result.items()}
    if current_taocan_check_result:
        log.info(f'huiji_detect camera source:{conf.huiji_detect_config['camera_source']} detect results:{current_taocan_check_result}')
    img = results.plot()

    return array2jpg(img)

def data_source():
    def get_ds(detect_config):
        data_source_type = detect_config['data_source_type']
        if data_source_type == 'camera':
            data_source = detect_config['camera_source']
            if str(data_source).isdigit():
                data_source = int(data_source)
            return data_source
        else:
            return detect_config['video_file']
        
    if conf.current_mode == "huiji_detect":
        return get_ds(conf.huiji_detect_config)
    else:
        return get_ds(conf.person_detect_config)
        


def capture_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(data_source())
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



get_model(conf.huiji_detect_config['model'])

def array2jpg(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()


def changed(detect_result):
    return detect_result != last_taocan_check_result


