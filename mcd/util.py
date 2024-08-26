from functools import wraps
import threading
import cv2

# 获取视频播放时长(秒)
def get_video_time(vidoe_file):
    # 读取视频文件
    cap = cv2.VideoCapture(vidoe_file)

    # 获取视频的总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 获取视频的 FPS (每秒的帧数)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 计算视频的播放时长（秒）
    return total_frames / fps


# 函数单例执行装饰器
def singleton_execution(func):
    lock = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper

