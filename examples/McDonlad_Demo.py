
from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.pt")  # load an official detection model
# model = YOLO("yolov8n-seg.pt")  # load an official segmentation model

# Track with the modelp
# source = sys.argv[1]
# results = model.track(source=source, show=False,save=True,classes=[0])

# source=1 ,代表从1号摄像头捕获数据
#results = model.track(source=1, show=True, tracker="bytetrack.yaml")


# train model
model.train(data="coco8.yaml", epochs=3)
metrics = model.val()
results = model("https://ultralytics.com/images/bus.jpg")
path = model.export(format="onnx")

