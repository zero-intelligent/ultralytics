import cv2
from ultralytics import YOLO
import mcd.conf as conf
from mcd.logger import log


models = {}

def get_model(model_path):
    if not models.get(model_path):
        models[model_path] = YOLO(model_path)
    return models[model_path]

def person_detect_frame(frame):
    person_detect_model = get_model(conf.person_detect_config['model'])
    results = person_detect_model(frame,classes=[0])
    img = results[0].plot()
    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    return (frame,img)

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

def combo_meal_detect_frame(frame):
    img=None
    meal_result=None

    # huiji_detect_model = get_model(conf.huiji_detect_config['model'])
    # results = huiji_detect_model(frame,classes=[0])
    # meal_result = {}
    # for result in results:
    #     # 提取每个检测结果的 id 和 class 信息
    #     for obj in result.boxes:
    #         obj_id = obj.id.item() if hasattr(obj, 'id') else None
    #         obj_class = obj.cls.item()
    #         if obj_class not in meal_result:
    #             meal_result[obj_class]=set()
    #         meal_result[obj_class].add(obj_id)

    # meal_result = {k:len(v) for k,v in meal_result.items()}
    # img = results[0].plot()

    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    return (frame,img,meal_result)



def huiji_detect_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(conf.huiji_detect_config['camera_source'])
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield combo_meal_detect_frame(frame)

    cap.release()




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