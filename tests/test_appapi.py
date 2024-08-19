import pytest
import httpx
from fastapi.testclient import TestClient
from api.app import app  

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

def test_capture_addr():
    response = client.get("/capture_addr")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data'] == 0

    response = client.post("/capture_addr",json="0")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
    assert json['data']['capture_addr'] == "0"


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
    #client.get("/huiji_video_output_feed")
    response = client.get("/huiji_video_taocan_detect_result")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 1

@pytest.mark.skip()
def test_huiji_video_output_feed():
    response = client.get("/huiji_video_output_feed")
    assert response.status_code == 200
    assert response.headers["content-type"] == 'ultipart/x-mixed-replace; boundary=frame'
    stream = response.iter_bytes()

    assert b'Content-Type: image/jpeg' in next(stream)
    assert b'Content-Type: image/jpeg' in next(stream)
    assert b'Content-Type: image/jpeg' in next(stream)

