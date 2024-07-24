
from ultralytics import YOLO
import sys

print(sys.path)

# Load a model
model = YOLO("yolov8n.pt")  # load an official detection model
# model = YOLO("yolov8n-seg.pt")  # load an official segmentation model

# Track with the modelp
results = model.track(source="/Users/mac/Downloads/crashing_in_shop.mp4", show=True,save=True,classes=[0])

# source=1 ,代表从1号摄像头捕获数据
#results = model.track(source=1, show=True, tracker="bytetrack.yaml")


