import json
import os
from mcd.logger import log

# 当前的分析模式 套餐汇集分析：huiji_detect, 大厅人员检测分析：person_detect
current_mode = 'huiji_detect' 

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
        (0,'Breakfast','早餐'),
        (1,'Burger with Box','汉堡（盒装）'),
        (2,'Burger with Package','汉堡（包装）'),
        (3,'Burger','汉堡'),
        (4,'Cold Drink','冷饮'),
        (5,'Crispy Thighs','脆鸡腿'),
        (6,'Curly Fries','薯卷'),
        (7,'Fresh Corn Cup','玉米杯'),
        (8,'Fries','薯条'),
        (9,'Hash Browns','薯饼'),
        (10,'Hot Drink','热饮'),
        (11,'McFlurry','麦旋风'),
        (12,'McNuggets','麦乐鸡'),
        (13,'McWings','麦翅'),
        (14,'Pie','派'),
        (15,'Sundae','圣代'),
        (16,'Twist Cone','甜筒'),
        (17,'Twisty Pasta Box','意面（盒装）'),
        (18,'Twisty Pasta','意面'),
        (19,'breakfast box','早餐盒'),
        (20,'salad','沙拉')
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

def data_source():
    detect_config = current_detect_config()
    data_source_type = detect_config['data_source_type']
    if data_source_type == 'camera':
        data_source = detect_config['camera_source']
        if str(data_source).isdigit():
            data_source = int(data_source)
        return data_source
    else:
        return detect_config['video_file']
    

def current_detect_config():
    if current_mode == 'huiji_detect':
        return huiji_detect_config
    else:
        return person_detect_config
    
config_file = 'mcd_conf.json'

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r',encoding='utf-8') as config_file1:
            conf = json.load(config_file1)
            log.info(f'load {config_file}, conents:{conf}')
        global current_mode,huiji_detect_config,person_detect_config
        current_mode = conf['current_mode']
        huiji_detect_config = conf['huiji_detect_config']
        person_detect_config = conf['person_detect_config']

def save_config():
    conf = {
        'current_mode': current_mode,
        'huiji_detect_config': huiji_detect_config,
        'person_detect_config': person_detect_config
    }
    with open(config_file, 'w',encoding='utf-8') as json_file:
        json.dump(conf, json_file, indent=4,ensure_ascii=False)
        log.info(f'save {config_file}, conents:{conf}')