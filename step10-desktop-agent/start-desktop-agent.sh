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

echo "===== STEP9 Claude Code ====="
date

echo "===== Configure code-server ====="
python3 /root/configure-desktop-agent.py

echo "===== Claude Code ====="

claude --version || true
node --version
npm --version

echo "===== Starting ttyd ====="
/usr/local/bin/ttyd \
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

echo "===== Starting code-server ====="
code-server \
  --config /root/.config/code-server/config.yaml \
  /root/workspace \
  >/tmp/code-server.log 2>&1 &

sleep 10

echo "===== Starting Firefox ====="
firefox \
  --no-remote \
  --new-window \
  http://127.0.0.1:8081 \
  >/tmp/firefox.log 2>&1 &

sleep 20

echo "Waiting for desktop windows..."
sleep 30

echo "===== Running Desktop Observer ====="
python3 /root/workspace/desktop_observer.py \
  >/tmp/desktop-observer.log 2>&1 || true

echo "===== Running Desktop Controller Demo ====="
python3 /root/workspace/desktop_controller.py \
  >/tmp/desktop-controller.log 2>&1 || true

echo "===== Process ====="
ps -ef | grep -E 'ttyd|Xvfb|x0vncserver|code-server|firefox|websockify' | grep -v grep || true

echo "===== code-server log ====="
tail -100 /tmp/code-server.log || true

echo "===== Firefox log ====="
tail -50 /tmp/firefox.log || true

echo "===== Desktop Observer log ====="
tail -100 /tmp/desktop-observer.log || true

echo "===== Desktop Controller log ====="
tail -100 /tmp/desktop-controller.log || true

echo "===== Starting noVNC ====="
cd /opt/novnc
exec ./utils/novnc_proxy --listen 6080 --vnc localhost:5900
