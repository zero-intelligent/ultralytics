import pytest
from fastapi.testclient import TestClient
from api.app import app  

client = TestClient(app)

def test_get_capture_addr():
    response = client.get("/capture_addr")
    assert response.status_code == 200
    json =  response.json()
    assert json['code'] == 0
