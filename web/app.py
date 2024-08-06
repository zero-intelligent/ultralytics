from fastapi import FastAPI
from ultralytics import YOLO

app = FastAPI()


@app.post("/yolo/track")
async def track(uri: str):
    model = YOLO("yolov8n.pt")  # load an official detection model
    results = model.track(source=uri, show=False, save=True, classes=[0])
    # model.track(source=, show=True, tracker="bytetrack.yaml")

    return {"message": "server model tracking"}


@app.get("/yolo/check")
async def check_server():
    return {"message": "server enabled"}
