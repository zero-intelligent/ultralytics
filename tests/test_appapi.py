import pytest
import httpx
from fastapi.testclient import TestClient
from api.app import app  

client = TestClient(app)

@pytest.mark.skip()
def test_demo():
    response = client.get("/start")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0

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
    assert json['data']['current_taocan_result'] == {}


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



def test_pvideo_source_feed():
    response = client.get("/")
    assert response.status_code == 200
    
    response = client.get("/person_video_source_feed")
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/jpeg'