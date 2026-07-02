#!/usr/bin/env bash
set -euo pipefail

exec > >(tee -a /tmp/start.log) 2>&1

export DISPLAY=:1
export HOME=/root
export XDG_RUNTIME_DIR=/tmp/runtime-root
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
export TZ=Asia/Tokyo
export NO_AT_BRIDGE=1

mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

echo "===== STEP5 Firefox ====="
date
firefox --version

Xvfb :1 -screen 0 1280x720x24 -nolisten tcp &
sleep 2

mkdir -p ~/.vnc
printf "microvm\nmicrovm\nn\n" | vncpasswd

x0vncserver \
  -display :1 \
  -rfbport 5900 \
  -PasswordFile ~/.vnc/passwd \
  -SecurityTypes VncAuth &

sleep 2

firefox \
  --no-remote \
  --new-window \
  https://www.google.com \
  >/tmp/firefox.log 2>&1 &

sleep 5

ps aux | grep -E 'Xvfb|firefox|vnc' | grep -v grep || true
tail -50 /tmp/firefox.log || true

cd /opt/novnc
exec ./utils/novnc_proxy --listen 6080 --vnc localhost:5900
