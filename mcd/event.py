import asyncio

#配置和结果变化事件
config_changed_event = asyncio.Event()

#检测结果生成事件
result_frame_arrive_event = asyncio.Event()

