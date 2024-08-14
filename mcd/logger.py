import os
import logging
import colorlog

# 创建 logger
log = logging.getLogger("mcd")
log.setLevel(logging.INFO)

# 创建控制台处理器，并设置日志级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.addFilter(logging.Filter('mcd'))

# 创建日志格式器
formatter = colorlog.ColoredFormatter(
    '%(log_color)s[%(asctime)s] [%(levelname)s] [%(process)d %(filename)s:%(lineno)d] %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
)

# 设置控制台处理器的格式器
console_handler.setFormatter(formatter)

logfile = 'logs/mcd.log'
os.makedirs(os.path.dirname(logfile),exist_ok=True)
file_handler = logging.FileHandler(filename=logfile)
file_handler.setFormatter(formatter)

# 将控制台处理器添加到 logger
log.addHandler(console_handler)
log.addHandler(file_handler)


# 示例日志消息
# log.debug('This is a debug message')
# log.info('This is an info message')
# log.warning('This is a warning message')
# log.error('This is an error message')
# log.critical('This is a critical message')
