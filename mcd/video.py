import cv2

def analyze_frames(source=0):
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