import cv2
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # 使用 YOLOv8n 预训练模型


def get_available_cameras(max_cameras=10):
    available_cameras = []
    for camera_id in range(max_cameras):
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            available_cameras.append(camera_id)
            cap.release()  # 释放摄像头
    return available_cameras

def analyze_frames(source=0):
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 进行目标检测
        results = model(frame,classes=[0])
        annotated_frame = results[0].plot()  # 在帧上绘制检测结果
        
        # 编码帧为JPEG格式
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        yield buffer.tobytes()

    cap.release()
    
def gray_frames(source=0):
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理帧的地方，示例中我们将帧转换为灰度
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 编码帧为JPEG格式
        ret, buffer = cv2.imencode('.jpg', frame)
        yield buffer.tobytes()

    cap.release()
    
    
def capture_frames(source=0):
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 编码帧为JPEG格式
        ret, buffer = cv2.imencode('.jpg', frame)
        yield buffer.tobytes()

    cap.release()