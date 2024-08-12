import asyncio
import cv2
from ultralytics import YOLO

person_detect_model = YOLO('yolov8x.pt')  # 使用 YOLOv8n 预训练模型
combo_meal_detect_model = YOLO('mcd/combo_meal_detect_model.yolo')  # 使用 YOLOv8n 预训练模型

def start_combo_meal_detect(source):
    detect_mcd_packages_frames(source)

def detect_person_frames(source=0,bufferTransform=None):
    def person_detect_frame(frame):
        results = person_detect_model(frame,classes=[0])
        return results[0].plot()  # 在帧上

    return capture_frames(source,
                          frameTransform=person_detect_frame,
                          bufferTransform=bufferTransform)


def detect_mcd_packages_frames(source=0,bufferTransform=None):

    def combo_meal_detect_frame(frame):
        results = person_detect_model(frame,classes=[0])

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
        events_publisher.trigger_event('combo_meal_img_detected',img)
        return img

    return capture_frames(source,
                          frameTransform=combo_meal_detect_frame,
                          bufferTransform=bufferTransform)
    

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

def capture_frames(source=0,frameTransform=None,bufferTransform=None):
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
        
        if bufferTransform:
            buffer = bufferTransform(buffer)
        yield buffer.tobytes()

    cap.release()

