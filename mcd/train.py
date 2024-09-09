
from ultralytics import YOLO
from datetime import datetime

# Load a model
model = YOLO("yolov8n.pt")  # load an official detection model
# train model
save_dir = f"runs/detect/{datetime.now():%Y-%m-%d.%H}"
model.train(data="datasets/MCD/data.yaml", epochs=100,save=True,save_dir=save_dir)
metrics = model.val()

test_files = ["assets/taocan1.jpg",
              "assets/taocan2.jpg"]

results = model(test_files,save=True,save_dir=save_dir)

