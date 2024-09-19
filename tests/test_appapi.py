import asyncio
import multiprocessing
import pytest
import os
import time
from fastapi.testclient import TestClient
from mcd.domain_entities import DataSourceType, Mode
from ultralytics import YOLO
from mcd.api import app  
from mcd import conf
from mcd.logger import log
import mcd.video_srv as video_srv
from mcd.util import get_video_time

client = TestClient(app)

def test_yolo():
    model = YOLO("yolov8n.pt")
    results = model.track(source=0, stream=True,verbose=False)
    results = model.track(source='uploads/demo.mp4', stream=True,verbose=False)
    log.info("end.")


    
def test_switch_mode():
    response = client.get("/api/switch_mode?mode=huiji_detect")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0


def test_available_cameras():
    response = client.get("/api/available_cameras")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert len(json['data']) > 0

def test_mode_datasource():
    response = client.post("/api/mode_datasource",json={
        'mode': Mode.HUIJI.value,
        'data_source_type':DataSourceType.CAMERA.value,
        'data_source':'23'
    })
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

    response = client.get("/api/mode_datasource")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['mode'] == Mode.HUIJI.value
    assert json['data']['data_source_type'] == DataSourceType.CAMERA.value
    assert int(json['data']['data_source']) == 23

def test_taocans():
    response = client.get("/api/taocans")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert len(json['data']['taocans']) == 2
    assert json['data']['current_taocan_id'] == 0

def test_switch_taocan():
    response = client.post("/api/mode_datasource",json={
        'mode':Mode.HUIJI.value,
        'data_source_type':DataSourceType.CAMERA.value,
        'data_source':'0'
    })
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    
    response = client.get("/api/switch_taocan?taocan_id=1")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    
    response = client.get("/api/get_config")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['taocan_id'] == 1
    
def http_get(url):
    response = client.get(url)
    assert response.status_code == 200
    
def test_get_config():
    response = client.post("/api/mode_datasource",json={
        'mode':Mode.HUIJI.value,
        'data_source_type':DataSourceType.VIDEO_FILE.value,
        'data_source':'assets/demo_short.mp4'
    })
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    
    response = client.get("/api/get_config")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    
    process1 = multiprocessing.Process(name="video_source",target=http_get,args=(json['data']['video_source'],),daemon=True)
    process2 = multiprocessing.Process(name="video_target",target=http_get,args=(json['data']['video_target'],),daemon=True)
    
    process1.start()
    process2.start()
    
    # 休息10秒，等待yolo启动, 获取到套餐检测结果
    total_seconds = 0
    while True:
        log.info(f"wait 2s to 等到摄像头启动, 获取到套餐检测结果.")
        time.sleep(2)
        total_seconds += 2
        response = client.get("/api/get_config")
        assert response.status_code == 200
        json =  response.json()
        assert json['code'] == 0
        if len(json['data']['current_taocan_result']) > 0 and total_seconds < 60:
            break
        assert total_seconds < 60000 or len(json['data']['current_taocan_result']) > 0, f"超过 {total_seconds}s 依然未获取到检测结果，测试失败!"
    
    results = json['data']['current_taocan_result']
    log.info(results)
    assert len(results) > 0
    assert 'id' in results[0].keys()
    assert 'name' in results[0].keys()
    assert 'real_count' in results[0].keys()
    assert 'lack_item' in results[0].keys()
    assert 'lack_count' in results[0].keys()

    if results[0]['lack_item']:
        assert results[0]['real_count'] == 0
    else:
        assert results[0]['real_count'] >= 1
        
    process1.terminate()
    process2.terminate()
        

def test_huiji_video_taocan_detect_result():
    response = client.get("/api/huiji_video_taocan_detect_result")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0



def test_upload_file():
    file_path = "assets/demo_short.mp4"  # 替换为实际文件路径
    with open(file_path, "rb") as file:
        response = client.post("/api/single_upload", files={"file": file})
    assert response.status_code == 200
    assert response.json()["filename"] == "demo_short.mp4"
    assert os.path.exists("uploads/demo_short.mp4")

    response = client.get("/api/mode_datasource")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['data_source_type'] == DataSourceType.VIDEO_FILE.value
    assert json['data']['data_source'] == 'uploads/demo_short.mp4'



def test_video_source_feed():
    video_file = 'assets/demo_short.mp4'
    
    response = client.post("/api/mode_datasource",json={
        'mode':Mode.HUIJI.value,
        'data_source_type':DataSourceType.VIDEO_FILE.value,
        'data_source':video_file
    })
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

    assert conf.huiji_detect_config['video_file'] == video_file
    
    time_s = get_video_time(video_file)
    
    log.info(f'{video_file} time {time_s}s')
    
    
    
    start = time.time()
    # video_srv.capture_frames()
    stream_time = time.time() - start
    
    log.info(f'{video_file} capture_frames time {stream_time}s')
    

    


