#!/bin/bash
# Roda NA EC2 (Amazon Linux 2023): sudo bash /opt/app/deploy/setup_ec2.sh
# Pré-requisito: código em /opt/app e /opt/app/.env criado (ver README).
set -e
dnf install -y python3-pip mariadb105
python3 -m venv /opt/app/venv
/opt/app/venv/bin/pip install -r /opt/app/backend/requirements.txt

cat > /etc/systemd/system/vet-api.service <<UNIT
[Unit]
Description=API Clinica Vet
After=network.target
[Service]
WorkingDirectory=/opt/app/backend
EnvironmentFile=/opt/app/.env
ExecStart=/opt/app/venv/bin/gunicorn -b 0.0.0.0:80 -w 2 app:app
Restart=always
[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now vet-api
sleep 2
systemctl status vet-api --no-pager
