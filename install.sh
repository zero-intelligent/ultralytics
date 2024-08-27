#!/bin/bash

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