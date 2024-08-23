import pytest
import os
import time
from fastapi.testclient import TestClient
from api.app import app  
from mcd import conf
import mcd.video as video_srv
from mcd.util import get_video_time

client = TestClient(app)


def test_switch_mode():
    response = client.get("/switch_mode?mode=huiji_detect")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0


def test_available_cameras():
    response = client.get("/available_cameras")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert len(json['data']) > 0

def test_mode_datasource():
    response = client.post("/mode_datasource",json={
        'mode':'huiji_detect',
        'data_source_type':'camera',
        'data_source':'0'
    })
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

    response = client.get("/mode_datasource")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['mode'] == 'huiji_detect'
    assert json['data']['data_source_type'] == 'camera'
    assert int(json['data']['data_source']) == 0

def test_taocans():
    response = client.get("/taocans")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert len(json['data']['taocans']) == 2
    assert json['data']['current_taocan_id'] == 0

def test_switch_taocan():
    response = client.get("/switch_taocan?taocan_id=1")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

    
def test_taocan_analysis():
    response = client.get("/taocan_analysis")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    results = json['data']['current_taocan_result']
    print(results)
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
        

def test_person_analysis():
    response = client.get("/person_analysis")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

def test_huiji_video_taocan_detect_result():
    response = client.get("/huiji_video_taocan_detect_result")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 1



def test_upload_file():
    file_path = "assets/demo.mp4"  # 替换为实际文件路径
    with open(file_path, "rb") as file:
        response = client.post("/single_upload", files={"file": file})
    assert response.status_code == 200
    assert response.json()["filename"] == "demo.mp4"
    assert os.path.exists("uploads/demo.mp4")

    response = client.get("/mode_datasource")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['data_source_type'] == 'video_file'
    assert json['data']['data_source'] == 'uploads/demo.mp4'



def test_video_source_feed():
    video_file = 'assets/demo.mp4'
    
    response = client.post("/mode_datasource",json={
        'mode':'huiji_detect',
        'data_source_type':'video_file',
        'data_source':video_file
    })
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

    assert conf.huiji_detect_config['video_file'] == video_file
    
    time_s = get_video_time(video_file)
    
    print(f'{video_file} time {time_s}s')
    
    
    
    start = time.time()
    video_srv.capture_frames()
    stream_time = time.time() - start
    
    print(f'{video_file} capture_frames time {stream_time}s')
    

    start = time.time()
    response = client.get("/video_source_feed")
    assert response.status_code == 200 
    
    stream_time = time.time() - start
    
    print(f'{video_file} stream time {stream_time}s')
    
    assert time_s * 1.2 > stream_time >= time_s
    
    
    response = client.get("/get_config")
    assert response.status_code == 200 
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['frame_rate'] > 1
       
    
    
    response = client.get("/video_output_feed")
    assert response.status_code == 200
    


