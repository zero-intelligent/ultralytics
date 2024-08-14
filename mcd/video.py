import asyncio
import cv2
from ultralytics import YOLO
import mcd.conf as conf
from mcd.logger import log


async def start():
    global cap
    if cap:
        cap.release()
    if conf.current_mode == "huiji_detect":
        await capture_frames(conf.huiji_detect_config['camera_source'])
    else:
        await capture_frames(conf.person_detect_config['camera_source'])

models = {}

def get_model(model_path):
    global models
    if not models.get(model_path):
        models[model_path] = YOLO(model_path)
    return models[model_path]

def get_detect_person_frames_stream(padframe=None):
    def person_detect_frame(frame):
        person_detect_model = get_model(conf.person_detect_config['model'])
        results = person_detect_model(frame,classes=[0])
        img = results[0].plot()
        if padframe:
            img = padframe(img)
        return img

    return stream_generator("source_frame",person_detect_frame)


def get_detect_mcd_packages_frames_stream(padframe=None):
    
    def combo_meal_detect_frame(frame):
        huiji_detect_model = get_model(conf.huiji_detect_config['model'])
        results = huiji_detect_model(frame,classes=[0])
        meal_result = {}
        for result in results:
            # 提取每个检测结果的 id 和 class 信息
            for obj in result.boxes:
                obj_id = obj.id.item() if hasattr(obj, 'id') else None
                obj_class = obj.cls.item()
                if obj_class not in meal_result:
                    meal_result[obj_class]=set()
                meal_result[obj_class].add(obj_id)

        meal_result = {k:len(v) for k,v in meal_result.items()}
        img = results[0].plot()
        if padframe:
            img = padframe(img)
        return (img,meal_result)

    return stream_generator("source_frame",combo_meal_detect_frame)
    

class EventPublisher:
    def __init__(self):
        self.callbacks = {}

    def subscribe(self, event_name, callback):
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)

    def trigger_event(self, event_name, *args, **kwargs):
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                callback(*args, **kwargs)

events_publisher = EventPublisher()


def stream_generator(event_name,wrapper_frame=None):
    # 创建一个局部的 asyncio.Queue
    queue = asyncio.Queue()

    def event_callback(frame):
        # 将数据推送到局部的 queue 中
        asyncio.create_task(queue.put(frame))

    events_publisher.subscribe(event_name, event_callback)

    async def event_generator():
        try:
            while True:
                # 从局部 queue 中取出数据并发送
                data = await queue.get()
                if wrapper_frame:
                    data = wrapper_frame(data)
                yield data
        finally:
            # 处理清理逻辑，比如当客户端断开时，取消订阅等
            pass
    return event_generator



cap = None

async def capture_frames(source=0):
    log.info("==== capture_frames ====")
    global cap
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        events_publisher.trigger_event('source_frame',frame)
        ret, buffer = cv2.imencode('.jpg', frame)  # 编码帧为JPEG格式
        events_publisher.trigger_event('source_frame_img',buffer.tobytes())
    cap.release()