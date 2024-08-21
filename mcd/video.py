import logging
from ultralytics import YOLO
import cv2
import os
import mcd.conf as conf
from mcd.logger import log
from pathlib import Path
from mcd.custom_result import PersonResults


models = {}

def get_model(model_path):
    if not models.get(model_path):
        models[model_path] = YOLO(model_path)
    return models[model_path]

def person_detect_frame(frame):
    person_detect_model = get_model(conf.person_detect_config['model'])
    results = person_detect_model.track(frame,classes=[0],verbose=False)
    results[0].__class__ = PersonResults
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
    
    in_tancan_results = [
        {
            'id': t[0],
            'name': full_name(t[1]),
            'count': t[2],
            'real_count': detect_result[id] if t[0] in detect_result else 0,
            'lack_item': t[0] not in detect_result,
            'lack_count': t[0] in detect_result and  detect_result[t[0]] < t[2],
            'is_in_taocan': True
        } for t in taocan['items']
    ]

    def get_id_by_name(name):
        ids = [i[0] for i in conf.huiji_detect_config['meals_info'] if i[1] == name]
        return ids[0] if ids else None

    out_tancan_results = [
        {
            'id': get_id_by_name(name),
            'name': full_name(name),
            'count': None,
            'real_count': count,
            'lack_item': None,
            'lack_count': None,
            'is_in_taocan': False
        } for name,count in detect_result.items() if name not in [i['name'] for i in taocan['items']]
    ]
    return in_tancan_results + out_tancan_results


last_taocan_check_result = None
current_taocan_check_result = None

def huiji_detect_frame(frame):
    img=None
    meal_result=None

    huiji_detect_model = get_model(conf.huiji_detect_config['model'])
    results = huiji_detect_model(frame,verbose=False) 
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
        log.info(f'camera source:{conf.huiji_detect_config['camera_source']} detect results:{current_taocan_check_result}')
    img = results[0].plot()

    return (array2jpg(frame),array2jpg(img),current_taocan_check_result)



def huiji_detect_frames():
    # 打开摄像头
    cap = cv2.VideoCapture(normal_camera_source())
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield huiji_detect_frame(frame)

    cap.release()

model_result_save_dir = "analysis_video_output"
import os;os.makedirs(model_result_save_dir,exist_ok=True)

def analysis_huiji_video_file():
    conf.huiji_detect_config['video_model_output_file'] = ''
    datasource = conf.huiji_detect_config['video_file']
    model = get_model(conf.huiji_detect_config['model'])
    results = model.track(datasource,save=True, verbose=False)

    model_output_file = Path(results[0].save_dir) / Path(datasource).name
    model_output_target_file = Path(model_result_save_dir) / Path(datasource).name
    model_output_target_file.write_bytes(model_output_file.read_bytes())  # 复制文件
    conf.huiji_detect_config['video_model_output_file'] = str(model_output_target_file)
        

def analysis_person_video_file():
    conf.huiji_detect_config['video_model_output_file'] = ''
    datasource = conf.huiji_detect_config['video_file']
    model = get_model(conf.huiji_detect_config['model'])
    results = model.track(datasource, verbose=True)

    # 获取输入视频的帧率和尺寸
    input_video = cv2.VideoCapture(datasource)
    fps = input_video.get(cv2.CAP_PROP_FPS)
    width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 定义输出视频文件路径和编码器
    output_file = Path(model_result_save_dir) / Path(datasource).name
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_file), fourcc, fps, (width, height))

    # 遍历结果并保存每帧图像
    for result in results:
        result.__class__ = PersonResults
        img = result.plot()
        out.write(img)

    # 释放资源
    out.release()
    input_video.release()

    conf.person_detect_config['video_model_output_file'] = str(output_file)


def analysis_video_file():
    if conf.current_mode == "huiji_detect":
        analysis_huiji_video_file()
    else:
        analysis_person_video_file()


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