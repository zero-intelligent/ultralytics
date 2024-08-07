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

    
def detect_frame(frame):
    results = model(frame,classes=[0])
    return results[0].plot()  # 在帧上

def detect_person_frames(source=0,bufferTransform=None):
    return capture_frames(source,
                          frameTransform=detect_frame,
                          bufferTransform=bufferTransform)
    
def detect_mcd_packages_frames(source=0,bufferTransform=None):
    return capture_frames(source,
                          frameTransform=detect_frame,
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