#!/usr/bin/env bash

CONFIGS_DIR="/etc/opid"
SETTINGS="${CONFIGS_DIR}/settings.py"

mkdir -p "$CONFIGS_DIR"
chmod 755 "$CONFIGS_DIR"

groupadd opid

cp ./opid.py /usr/bin/opid
chmod 755 /usr/bin/opid

cp ./settings.py "$SETTINGS"

cp ./opid.service /etc/systemd/system/

systemctl daemon-update
systemctl enable opid
systemctl start opid