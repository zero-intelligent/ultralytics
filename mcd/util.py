from functools import wraps
import threading
import cv2
import yaml
from cProfile import Profile
from pstats import SortKey, Stats


def update_yaml(yaml_file, **kwargs):
    # 加载 YAML 文件到字典
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    data |= kwargs

    # 保存修改后的字典回 YAML 文件
    with open(yaml_file, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
        
        
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

# 函数性能分析装饰器
def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Profile() as profile:
            ret = func(*args, **kwargs)
            Stats(profile).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)
            Stats(profile).strip_dirs().sort_stats(SortKey.TIME).print_stats(20)
            Stats(profile).strip_dirs().sort_stats(SortKey.CALLS).print_stats(20)
            return ret
    return wrapper
            