import platform
import subprocess
import re
import cv2
import objc
from AppKit import AVCaptureDevice


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

def get_cameras_linux():
    camera_list = []

    # Try to open a large number of camera indices
    for camera_id in range(10):
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            camera_name = f"Camera {camera_id}"
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
        return get_cameras_windows()
    elif os_type == "Linux":
        return get_cameras_linux()
    elif os_type == "Darwin":  # macOS
        return get_cameras_mac()
    else:
        print(f"Unsupported OS: {os_type}")
        return []
    


if __name__ == "__main__":

    cameras = get_cameras()
    for cam_id, cam_name in cameras:
        print(f"Camera ID: {cam_id}, Camera Name: {cam_name}")
