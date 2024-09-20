
from ultralytics import YOLO
from datetime import datetime
import sys
import os
from util import update_yaml

dataset_dir = sys.argv[1] if  len(sys.argv) == 2 else os.getcwd() + '/datasets/MCD'

# from ultralytics import YOLO;YOLO('runs/detect/2024-09-20.10/weights/best.pt').export(format='onnx')

def main():

    # train model
    save_dir = f"runs/detect/{datetime.now():%Y-%m-%d.%H}"
    yaml_file = dataset_dir + '/data.yaml'
    update_yaml(yaml_file, augment= {
        "flipud": 0.7,  # 随机垂直翻转的概率
        "fliplr": 0.7,  # 随机水平翻转的概率
        "hsv_h": 0.015,  # 色调（Hue）调整范围
        "hsv_s": 0.7,    # 饱和度（Saturation）调整范围
        "hsv_v": 0.4,    # 亮度（Value）调整范围
        "degrees": 0.0,  # 随机旋转的角度范围
        "translate": 0.1,  # 随机平移的比例
        "scale": 0.5,    # 随机缩放的比例
        "shear": 0.0,    # 随机剪切的角度
        "perspective": 0.0  # 透视变换的范围
    })
    
    # Load a model
    model = YOLO("yolov8n.pt")  # load an official detection model
    model.train(
        data=yaml_file, 
        epochs=100,
        batch=32,
        workers=8,
        save=True,
        save_dir=save_dir,
        augment=True)

    metrics = model.val()
    
    model.export(format="onnx")

    test_files = ["assets/taocan1.jpg",
                "assets/taocan2.jpg"]

    results = model(test_files,save=True,save_dir=save_dir)

if __name__ == "__main__":
    main()
