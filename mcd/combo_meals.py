
class MealItem:
    def __init__(self,id,name,cnt):
        self.id = id
        self.name =name
        self.cnt = cnt
    

class ComboMeal:
    def __init__(self,id,name,items):
        self.id = id
        self.name = name 
        self.items = items
        

# 食品清单信息：id,EnglishName, ChineseName
meals_info = [
    (0,'Fried Chicken','炸鸡'),
    (1,'Burgen','汉堡'),
    (3,'French Fries','薯条'),
    (4,'Large Coke','大杯可乐'),
    (5,'Medium Coke','中杯可乐'),
    (6,'Small Coke','小杯可乐')
]

# 预配置套餐信息
combo_meals = [
    {
        "id": 0,
        "name": '麦辣鸡腿汉堡中套餐',
        "items":[
            [0,'Burgen',1],
            [1,'French Fries',1]
            [2,'Large Coke',1]
        ]
    },
    {
        "id": 0,
        "name": '周末聚划算四人餐',
        "items":[
            [0,'Burgen',4],
            [1,'French Fries',1],
            [2,'Medium Coke',4],
            [3,'Chicken McNuggets',5]
        ]
    }
]

# 当前默认选中套餐
current_combo_meals = combo_meals[0]