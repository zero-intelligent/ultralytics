
from ultralytics import YOLO
from datetime import datetime

# Load a model
model = YOLO("yolov8n.pt")  # load an official detection model
# model = YOLO("yolov8n-seg.pt")  # load an official segmentation model

# Track with the modelp
# source = sys.argv[1]
# results = model.track(source=source, show=False,save=True,classes=[0])

# source=1 ,代表从1号摄像头捕获数据
#results = model.track(source=1, show=True, tracker="bytetrack.yaml")


# train model
save_dir = f"runs/detect/{datetime.now():%Y-%m-%d.%H}"
model.train(data="datasets/MCD/data.yaml", epochs=100,save=True,save_dir=save_dir)
metrics = model.val()
results = model("assets/taocan1.jpg",save=True,save_dir=save_dir)
results = model("assets/taocan2.jpg",save=True,save_dir=save_dir)



