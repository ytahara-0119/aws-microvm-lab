#!/usr/bin/env bash
set -euo pipefail

exec > >(tee -a /tmp/start.log) 2>&1

export DISPLAY="${DISPLAY:-:1}"
export HOME=/root
export XDG_RUNTIME_DIR=/tmp/runtime-root
export XDG_CURRENT_DESKTOP=XFCE
export LANG="${LANG:-ja_JP.UTF-8}"
export LC_ALL="${LC_ALL:-ja_JP.UTF-8}"
export TZ="${TZ:-Asia/Tokyo}"
export NO_AT_BRIDGE=1

mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

echo "===== STEP18 ParrotOS Desktop ====="
date
cat /etc/os-release || true

echo "===== Starting Xvfb ====="
Xvfb "$DISPLAY" -screen 0 "${GEOMETRY:-1280x800}x24" -nolisten tcp &
for _ in $(seq 1 100); do
  xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break
  sleep 0.1
done
xdpyinfo -display "$DISPLAY" >/dev/null

xset -display "$DISPLAY" s off -dpms || true

echo "===== Starting XFCE (dbus session) ====="
eval "$(dbus-launch --sh-syntax)"
startxfce4 &
sleep 3

echo "===== Starting x11vnc ====="
x11vnc \
  -display "$DISPLAY" \
  -forever \
  -shared \
  -noxdamage \
  -passwd "${VNC_PASSWORD:-microvm}" \
  -rfbport "${RFB_PORT:-5900}" &

sleep 2

echo "===== Starting MicroVM lifecycle hook server (port ${HOOK_PORT:-9000}) ====="
python3 /opt/microvm/hooks_server.py &

echo "===== Process snapshot ====="
ps aux | grep -E 'Xvfb|xfce|x11vnc|dbus|hooks_server' | grep -v grep || true

echo "===== Starting noVNC (port ${VNC_PORT:-6080}) ====="
cd /opt/novnc
exec ./utils/novnc_proxy \
  --listen "${VNC_PORT:-6080}" \
  --vnc "localhost:${RFB_PORT:-5900}"
