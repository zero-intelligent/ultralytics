import asyncio
import cv2
from ultralytics import YOLO
import mcd.conf as conf

async def start():
    if cap:
        cap.release()
    if conf.current_mode == "huiji_detect":
        detect_mcd_packages_frames(conf.huiji_detect_config['camera_source'])
    else:
        detect_person_frames(conf.person_detect_config['camera_source'])


def detect_person_frames(source=0):
    person_detect_model = YOLO(conf.person_detect_config['model'])
    def person_detect_frame(frame):
        results = person_detect_model(frame,classes=[0])
        img = results[0].plot()
        events_publisher.trigger_event('model_result_img_detected',img)
        return img

    return capture_frames(source,frameTransform=person_detect_frame)


def detect_mcd_packages_frames(source=0):
    huiji_detect_model = YOLO(conf.huiji_detect_config['model'])
    def combo_meal_detect_frame(frame):
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
        events_publisher.trigger_event('combo_meal_result_detected',meal_result)
        img = results[0].plot()
        events_publisher.trigger_event('model_result_img_detected',img)
        return img

    return capture_frames(source,frameTransform=combo_meal_detect_frame)
    

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


cap = None;

def capture_frames(source=0,frameTransform=None):
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        events_publisher.trigger_event('source_frame',frame)
        if frameTransform:
            frame = frameTransform(frame)
        # 编码帧为JPEG格式
        ret, buffer = cv2.imencode('.jpg', frame)
        yield buffer.tobytes()

    cap.release()

