import platform
import subprocess
import re
import cv2
from mcd.logger import log 

def check_camera_availability(camera_id=0):
    # 打开摄像头
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        log.error(f"无法打开摄像头 {camera_id}")
        return False

    # 读取一帧来检测摄像头的可用性
    ret, frame = cap.read()
    if not ret:
        log.error(f"摄像头 {camera_id} 无法读取帧")
        cap.release()
        return False

    # 释放资源
    cap.release()
    log.info(f"摄像头 {camera_id} 正常工作且可用")
    return True


def list_cameras():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

def get_cameras_windows():
    import win32com.client
    cameras = []
    device_manager = win32com.client.Dispatch('WMICool.WMICool')
    for device in device_manager.ExecQuery('SELECT * FROM Win32_PnPEntity'):
        if 'camera' in device.Name.lower():
            cameras.append((device.DeviceID, device.Name))
    return cameras

def get_cameras_linux(max_cameras=30):
    camera_list = []

    # Try to open a large number of camera indices
    for camera_id in range(max_cameras):
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            camera_name = f"/dev/video{camera_id}"
            camera_list.append((camera_id, camera_name))
            cap.release()
    return camera_list


def get_cameras_mac():
    try:
        # Execute the command
        result = subprocess.run(
            'system_profiler SPCameraDataType',
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Define a regex pattern to match camera names
        pattern = re.compile(r'\s{4}(.+):\n')

        # Find all matches in the command output
        camera_names = pattern.findall(result.stdout)
        return [(index,v) for index,v in enumerate(camera_names)]

    except subprocess.CalledProcessError as e:
        # Handle errors in command execution
        print(f"Error executing command: {e}")
        return []


def get_cameras():
    os_type = platform.system()
    
    if os_type == "Windows":
        result = get_cameras_windows()
    elif os_type == "Linux":
        result = get_cameras_linux()
    elif os_type == "Darwin":  # macOS
        result = get_cameras_mac()
    else:
        log.error(f"Unsupported OS: {os_type}")
        result = []
    
    return [(id,name) for id,name in result if check_camera_availability(id)]


if __name__ == "__main__":

    cameras = get_cameras()
    for cam_id, cam_name in cameras:
        print(f"Camera ID: {cam_id}, Camera Name: {cam_name}")
