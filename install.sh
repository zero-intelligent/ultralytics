#!/bin/bash

APP_HOME=`cd -P $(dirname "$0");pwd`
echo "APP_HOME=$APP_HOME"
# 安装文件路径
whl_file=./dist/ultralytics-8.2.63-py3-none-any.whl

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

if ! pip install "$whl_file"; then
    echo "Error: Failed to install $whl_file."
    exit 1
fi

# 安装服务
SERVICE_NAME="mcd-video-analysis"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# 创建服务单元文件
cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=$SERVICE_NAME
After=network.target

[Service]
Type=simple
ExecStart="mcd-video-analysis"
ExecStop="/usr/bin/pkill -f mcd-video-analysis"
Restart=always
User=admin
WorkingDirectory=$APP_HOME
Environment="PATH=/usr/local/bin:/usr/bin:/bin" "PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOL

# 重新加载 systemd 配置
systemctl daemon-reload

# 启动服务
systemctl start "$SERVICE_NAME"

# 设置为自动启动
systemctl enable "$SERVICE_NAME"

# 查看服务启动状态
systemctl status "$SERVICE_NAME"