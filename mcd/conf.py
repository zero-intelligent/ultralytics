import json
import os


# 当前的分析模式 套餐汇集分析：huiji_detect, 大厅人员检测分析：person_detect
current_mode = 'huiji_detect' 


huiji_detect_config = {

    # 当前摄像头地址，本地为 0,1,2， 网络是 uri 地址
    "camera_source": 0,

    # 当前选中的套餐id
    "current_combo_meals_id": 0,

    #当前使用的模型
    "model": "mcd/huiji_detect_model.pt",

    # 食品清单信息：id,EnglishName, ChineseName
    "meals_info": [
        (0,'Fried Chicken','炸鸡'),
        (1,'Burgen','汉堡'),
        (3,'French Fries','薯条'),
        (4,'Large Coke','大杯可乐'),
        (5,'Medium Coke','中杯可乐'),
        (6,'Small Coke','小杯可乐')
    ],

    # 预配置套餐信息
    "combo_meals": [
        {
            "id": 0,
            "name": '麦辣鸡腿汉堡中套餐',
            "items":[
                [0,'Burgen',1],
                [1,'French Fries',1],
                [2,'Large Coke',1]
            ]
        },
        {
            "id": 1,
            "name": '周末聚划算四人餐',
            "items":[
                [0,'Burgen',4],
                [1,'French Fries',1],
                [2,'Medium Coke',4],
                [3,'Chicken McNuggets',5]
            ]
        }
    ]
}

person_detect_config = {
    # 当前摄像头地址，本地为 0,1,2， 网络是 uri 地址
    "camera_source": 0,
    "model": "yolov8n.pt"

}



config_file = 'mcd_conf.json'

def load_config():
    if os.path.exists(config_file):
        conf = json.load(config_file)
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
    with open(config_file, 'w',encoding='utf8') as json_file:
        json.dump(conf, json_file, indent=4)