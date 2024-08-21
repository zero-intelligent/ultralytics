from ultralytics import YOLO
import cv2
import os
import mcd.conf as conf
from mcd.logger import log
from pathlib import Path


models = {}

def get_model(model_path):
    if not models.get(model_path):
        models[model_path] = YOLO(model_path)
    return models[model_path]

def person_detect_frame(frame):
    person_detect_model = get_model(conf.person_detect_config['model'])
    results = person_detect_model.track(frame,classes=[0])
    img = results[0].plot()
    return (array2jpg(frame),array2jpg(img))

def person_detect_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(normal_camera_source())
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield person_detect_frame(frame)

    cap.release()


get_model(conf.huiji_detect_config['model'])

def array2jpg(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()



def changed(detect_result):
    return detect_result != last_taocan_check_result

def get_detect_items(detect_result):
    taocan_id = conf.huiji_detect_config['current_taocan_id']
    taocan =  [t for t in conf.huiji_detect_config['taocans'] if t['id'] == taocan_id]
    if not taocan:
        raise Exception(f"can't find taocao with id:{taocan_id}")
    taocan = taocan[0]
    
    def full_name(name):
        full_names = [f'{i[2]} {i[1]}' for i in conf.huiji_detect_config['meals_info'] if i[1] == name]
        return full_names[0] if full_names else name
    
    return [
        {
            'id': t[0],
            'name': full_name(t[1]),
            'count': t[2],
            'real_count': detect_result[id] if t[0] in detect_result else 0,
            'lack_item': t[0] not in detect_result,
            'lack_count': t[0] in detect_result and  detect_result[t[0]] < t[2],
            'is_in_taocan': t[0] in detect_result
        } for t in taocan['items']
    ]

last_taocan_check_result = None
current_taocan_check_result = None

def combo_meal_detect_frame(frame):
    img=None
    meal_result=None

    huiji_detect_model = get_model(conf.huiji_detect_config['model'])
    results = huiji_detect_model(frame) # 需要确保图片尺寸一致
    meal_result = {}
    for result in results:
        # 提取每个检测结果的 id 和 class 信息
        for obj in result.boxes:
            obj_id = obj.id.item() if hasattr(obj, 'id') and obj.id else None
            obj_class = obj.cls.item()
            if obj_class not in meal_result:
                meal_result[obj_class]=set()
            meal_result[obj_class].add(obj_id)

    global current_taocan_check_result,last_taocan_check_result
    last_taocan_check_result = current_taocan_check_result
    current_taocan_check_result = {k:len(v) for k,v in meal_result.items()}
    img = results[0].plot()

    return (array2jpg(frame),array2jpg(img),current_taocan_check_result)



def huiji_detect_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(normal_camera_source())
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield combo_meal_detect_frame(frame)

    cap.release()

model_result_save_dir = "analysis_video_output"
import os;os.makedirs(model_result_save_dir,exist_ok=True)

def analysis_video_file():
    def analysis(detect_config):
        detect_config['video_model_output_file'] = ''
        datasource = detect_config['video_file']
        model = get_model(detect_config['model'])
        results = model.track(datasource,save=True)

        model_output_file = Path(results[0].save_dir) / Path(datasource).name
        model_output_target_file = Path(model_result_save_dir) / Path(datasource).name
        model_output_target_file.write_bytes(model_output_file.read_bytes())  # 复制文件
        detect_config['video_model_output_file'] = str(model_output_target_file)

    if conf.current_mode == "huiji_detect":
        analysis(conf.huiji_detect_config)
    else:
        analysis(conf.person_detect_config)


def normal_camera_source():
    camera_source = conf.huiji_detect_config['camera_source'] if conf.current_mode == "huiji_detect" else conf.person_detect_config['camera_source']
    if str(camera_source).isdigit():
        camera_source = int(camera_source)
    return camera_source

def capture_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(normal_camera_source())
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield frame

    cap.release()