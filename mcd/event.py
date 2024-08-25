import asyncio

#配置和结果变化事件
config_changed_event = asyncio.Event()

#汇集区检测
huiji_event = asyncio.Event()

# 人员检测
person_event = asyncio.Event()
