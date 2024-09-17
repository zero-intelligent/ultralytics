import json
import os
from mcd.domain_entities import DataSourceType, Mode
from mcd.logger import log

# 当前的分析模式 套餐汇集分析：huiji_detect, 大厅人员检测分析：person_detect
current_mode = Mode.HUIJI

drop_rate = 0.01

huiji_detect_config = {

    # 数据源类型，只可以是: 摄像头(camera)/视频文件(video_file)
    "data_source_type": "camera",

    # 当前摄像头地址，本地为 0,1,2， 网络是 uri 地址
    "camera_source": 0,

    "video_file": "",

    # 当前选中的套餐id
    "current_taocan_id": 0,

    #当前使用的模型
    "model": "mcd/huiji_detect_model.pt",

    # 食品清单信息：id,EnglishName, ChineseName
    "meals_info": [
        (0,'apple-juice','早餐'),
        (1,'cola','可乐'),
        (2,'jiroujuan','鸡肉卷'),
        (3,'juwuba','巨无霸汉堡'),
        (4,'kaochi','烤翅'),
        (5,'maileji','麦乐鸡'),
        (6,'maixuanfeng','麦旋风'),
        (7,'paper','餐巾纸'),
        (8,'shutiao','薯条'),
        (9,'tiansuan-jam','甜酸酱'),
        (10,'tomato-jam','番茄酱')
    ],

    # 预配置套餐信息
    "taocans": [
        {
            "id": 0,
            "name": '麦辣鸡腿汉堡中套餐',
            "items":[
                [3,'Burger',1],
                [12,'McNuggets',1],
                [4,'Cold Drink',1]
            ]
        },
        {
            "id": 1,
            "name": '周末聚划算四人餐',
            "items":[
                [3,'Burger',4],
                [8,'Fries',1],
                [11,'McFlurry',4],
                [14,'Pie',4],
            ]
        }
    ]
}


person_detect_config = {
    # 数据源类型，只可以是: 摄像头(camera)/视频文件(video_file)
    "data_source_type": "camera",
    # 当前摄像头地址，本地为 0,1,2， 网络是 uri 地址
    "camera_source": 0,
    "video_file": "",
    "model": "yolov8n.pt"

}

def current_detect_config():
    if current_mode == Mode.HUIJI:
        return huiji_detect_config
    else:
        return person_detect_config

def data_source():
    detect_config = current_detect_config()
    data_source_type = detect_config['data_source_type']
    if data_source_type == DataSourceType.CAMERA.value:
        data_source = detect_config['camera_source']
        if str(data_source).isdigit():
            data_source = int(data_source)
        return data_source
    else:
        return detect_config['video_file']
    

def configure_default_local_camera():
    from mcd.camera import get_cameras
    cameras = get_cameras()
    if not cameras:
        log.error("找不到可用的本地摄像头")
        return
    camera_id,camera_name = cameras[0]
    if not huiji_detect_config['camera_source']:
        huiji_detect_config['camera_source'] = camera_id
    if not person_detect_config['camera_source']:
        person_detect_config['camera_source'] = camera_id
        
    log.info(f"available local cameras:{cameras} \ndefault use: {cameras[0]},data_source:{data_source()}")
    

configure_default_local_camera()


    
config_file = 'mcd_conf.json'

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r',encoding='utf-8') as config_file1:
            conf = json.load(config_file1)
            log.info(f'load {config_file}, conents:{conf}')
        global current_mode,huiji_detect_config,person_detect_config
        current_mode = Mode(conf['current_mode'])
        huiji_detect_config = conf['huiji_detect_config']
        person_detect_config = conf['person_detect_config']

def save_config():
    conf = {
        'current_mode': current_mode.value,
        'huiji_detect_config': huiji_detect_config,
        'person_detect_config': person_detect_config
    }
    with open(config_file, 'w',encoding='utf-8') as json_file:
        json.dump(conf, json_file, indent=4,ensure_ascii=False)
        log.info(f'save {config_file}, conents:{conf}')