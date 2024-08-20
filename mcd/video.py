from ultralytics import YOLO
import cv2
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
    cap = cv2.VideoCapture(conf.person_detect_config['camera_source'])
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
    taocan =  conf.huiji_detect_config['taocans'][taocan_id]
    return [
        {
            'id': t[0],
            'name': t[1],
            'count': t[2],
            'real_count': detect_result[id] if id in detect_result else 0,
            'lack_item': id not in detect_result,
            'lack_count': id in detect_result and  detect_result[id] < t[2]
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
    cap = cv2.VideoCapture(conf.huiji_detect_config['camera_source'])
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield combo_meal_detect_frame(frame)

    cap.release()


def analysis_video_file():
    save_dir = 'analysis_video_output'
    if conf.mode == "huiji_detect":
        conf.huiji_detect_config['video_model_output_file'] = ''
        datasource = conf.huiji_detect_config['data_source']
        model = get_model(conf.huiji_detect_config['model'])
        results = model.track(datasource,save=True, save_dir=save_dir)
        conf.huiji_detect_config['video_model_output_file'] = str(Path(save_dir) / Path(datasource).name)
    else:
        conf.person_detect_config['video_model_output_file'] = ''
        datasource = conf.person_detect_config['data_source']
        model = get_model(conf.person_detect_config['model'])
        results = model.track(datasource,classes=[0],save=True, save_dir=save_dir)
        conf.person_detect_config['video_model_output_file'] = str(Path(save_dir) / Path(datasource).name)
    

def capture_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(conf.huiji_detect_config['camera_source'])
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield frame

    cap.release()