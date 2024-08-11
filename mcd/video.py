import cv2
import asyncio
from ultralytics import YOLO

person_detect_model = YOLO('yolov8x.pt')  # 使用 YOLOv8n 预训练模型
combo_meal_detect_model = YOLO('mcd/combo_meal_detect_model.yolo')  # 使用 YOLOv8n 预训练模型


def detect_person_frames(source=0,bufferTransform=None):
    def person_detect_frame(frame):
        results = person_detect_model(frame,classes=[0])
        return results[0].plot()  # 在帧上

    return capture_frames(source,
                          frameTransform=person_detect_frame,
                          bufferTransform=bufferTransform)

# 套餐结果检测结果队列
video_combo_meal_result_queue = asyncio.Queue()

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
        video_combo_meal_result_queue.put(meal_result)

        return results[0].plot()  # 在帧上

    return capture_frames(source,
                          frameTransform=combo_meal_detect_frame,
                          bufferTransform=bufferTransform)
    
def gray_frames(source=0,bufferTransform=None):
    return capture_frames(source,
                          lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                          bufferTransform)
    
    
def capture_frames(source=0,frameTransform=None, bufferTransform=None):
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frameTransform:
            frame = frameTransform(frame)
        # 编码帧为JPEG格式
        ret, buffer = cv2.imencode('.jpg', frame)
        
        if bufferTransform:
            buffer = bufferTransform(buffer)
        yield buffer.tobytes()

    cap.release()