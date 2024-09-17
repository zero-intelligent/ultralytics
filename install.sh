#!/bin/bash

APP_HOME=`cd -P $(dirname "$0");pwd`
echo "APP_HOME=$APP_HOME"

cd $APP_HOME
# 安装文件路径
whl_file=./dist/ultralytics-8.2.63-py3-none-any.whl

# 如果安全文件不存在，先去build一个
if [ ! -f "$whl_file" ]; then
    echo "Error: File $whl_file does not exist. begin to build. "
    if ! pip install -i https://mirrors.aliyun.com/pypi/simple build setuptools wheel; then
        echo "install module build setuptools wheel fail!"
        exit 1
    fi
    if ! python -m build; then
        echo "python -m build fail!"
        exit 1
    fi
fi

# 如果 $whl_file 已经安装，先卸载
pip uninstall "$whl_file" -y

# 安装 $whl_file 文件
if ! pip install --user "$whl_file" -i https://mirrors.aliyun.com/pypi/simple; then
    echo "Error: Failed to install $whl_file."
    exit 1
fi

# 安装服务
SERVICE_NAME="mcd-video-analysis"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# 创建服务单元文件
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=$SERVICE_NAME
After=network.target

[Service]
Type=simple
ExecStart=uvicorn mcd.api:app --host 0.0.0.0 --port 6789 --reload
ExecStop=/usr/bin/pkill -f uvicorn
Restart=always
User=$USER