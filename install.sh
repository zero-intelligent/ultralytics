#!/bin/bash

APP_HOME=`cd -P $(dirname "$0");pwd`
echo "APP_HOME=$APP_HOME"

cd $APP_HOME

# 删除中间缓存文件
rm -f mcd_conf.json
# 删除旧的日志
rm -rf logs

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
WorkingDirectory=$APP_HOME
Environment="PATH=/usr/local/bin:/usr/bin:/bin" "PYTHONUNBUFFERED=1" "PYTHONPATH=$APP_HOME"

[Install]
WantedBy=multi-user.target
EOL

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start "$SERVICE_NAME"

# 设置为自动启动
sudo systemctl enable "$SERVICE_NAME"


# 重新启动服务
sudo systemctl restart "$SERVICE_NAME"

sleep 2

# 查看服务启动状态
systemctl status "$SERVICE_NAME"





# 编译前端
cd $APP_HOME/gui

if ! npm run build; then
    echo "npm run build fail!"
    exit 1
fi


if grep -q "include $(pwd)/nginx.conf" /etc/nginx/nginx.conf; then
    echo "nginx 已包含正确配置"
else
    # 如果未包含，找到 http 节点的起始位置并添加 include 行
    sed -i "/http {/a\ $(printf '\n')    include $(pwd)/nginx.conf" /etc/nginx/nginx.conf
    nginx -t
    nginx -s reload
    echo "nginx 已正确配置"
fi
