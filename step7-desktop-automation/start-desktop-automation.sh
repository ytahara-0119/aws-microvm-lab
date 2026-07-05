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

echo "===== STEP7 Desktop Automation ====="
date
firefox --version
python3 --version
xdotool --version || true
wmctrl -V || true

echo "===== Starting ttyd ====="
ttyd \
  --port 7681 \
  --writable \
  bash &

sleep 2

echo "===== Starting Xvfb ====="
Xvfb :1 -screen 0 1280x720x24 -nolisten tcp &

sleep 2

echo "===== Starting TigerVNC ====="
mkdir -p ~/.vnc
printf "microvm\nmicrovm\nn\n" | vncpasswd

x0vncserver \
  -display :1 \
  -rfbport 5900 \
  -PasswordFile ~/.vnc/passwd \
  -SecurityTypes VncAuth &

sleep 2

echo "===== Starting Firefox ====="

firefox \
  --no-remote \
  --new-window \
  https://www.yahoo.co.jp \
  >/tmp/firefox.log 2>&1 &

sleep 30

echo "===== Running desktop observation ====="
python3 /root/demo_desktop.py > /tmp/desktop-observation.log 2>&1 &

sleep 5

echo "===== Process ====="
ps aux | grep -E 'Xvfb|firefox|vnc|python|xdotool|wmctrl' | grep -v grep || true

echo "===== Desktop Automation log ====="
tail -100 /tmp/desktop-automation.log || true

echo "===== Starting noVNC ====="
cd /opt/novnc
exec ./utils/novnc_proxy --listen 6080 --vnc localhost:5900
