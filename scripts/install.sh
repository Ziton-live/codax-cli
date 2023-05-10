#!/bin/bash
# mkdir ~/.codax && cd ~/.codax
# git clone https://github.com/Ziton-live/CODAX /tmp/codax-tmp
git -C "/tmp/codax-tmp" pull || git clone https://github.com/Ziton-live/CODAX "/tmp/codax-tmp"
# cd CODAX/src/_monitor
make -C /tmp/codax-tmp/src/_monitor container_tracer
cp /tmp/codax-tmp/src/_monitor/container_tracer /usr/bin

cat <<EOF > /etc/systemd/system/codax.service
[Unit]
Description= CODAX client for detecting CPU exhaustive DOS attacks 
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=10

[Service]
Type=simple
User=root
ExecStart=/usr/bin/container_tracer
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable codax.service
systemctl start codax.service

