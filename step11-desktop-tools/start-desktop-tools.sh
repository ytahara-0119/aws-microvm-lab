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
export PYTHONPATH=/root/workspace

mkdir -p "${XDG_RUNTIME_DIR}"
chmod 700 "${XDG_RUNTIME_DIR}"

echo "===== STEP11 Desktop Tools ====="
date

echo "===== Versions ====="
python3 --version
node --version
npm --version
git --version
claude --version || true
code-server --version || true

echo "===== Configure Desktop Tools ====="
python3 /root/configure-desktop-tools.py

echo "===== Starting ttyd ====="
/usr/local/bin/ttyd \
  --port 7681 \
  --writable \
  bash \
  >/tmp/ttyd.log 2>&1 &

sleep 2

echo "===== Starting Xvfb ====="
Xvfb :1 \
  -screen 0 1280x720x24 \
  -nolisten tcp \
  >/tmp/xvfb.log 2>&1 &

sleep 2

echo "===== Starting TigerVNC ====="
mkdir -p /root/.vnc

printf "microvm\nmicrovm\nn\n" | vncpasswd \
  >/tmp/vncpasswd.log 2>&1

x0vncserver \
  -display :1 \
  -rfbport 5900 \
  -PasswordFile /root/.vnc/passwd \
  -SecurityTypes VncAuth \
  >/tmp/x0vncserver.log 2>&1 &

sleep 2

echo "===== Starting code-server ====="
code-server \
  --config /root/.config/code-server/config.yaml \
  /root/workspace \
  >/tmp/code-server.log 2>&1 &

echo "Waiting for code-server..."

for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8081/ >/dev/null 2>&1; then
    echo "code-server is ready."
    break
  fi

  sleep 1
done

if ! curl -fsS http://127.0.0.1:8081/ >/dev/null 2>&1; then
  echo "WARNING: code-server readiness check timed out."
fi

echo "===== Starting Firefox ====="
firefox \
  --no-remote \
  --new-window \
  http://127.0.0.1:8081 \
  >/tmp/firefox.log 2>&1 &

echo "Waiting for desktop window..."

WINDOW_READY=false

for _ in $(seq 1 60); do
  if xwininfo -root -tree 2>/dev/null \
    | grep -Eq '"[^"]*(Firefox|code-server|workspace)[^"]*"'; then
    WINDOW_READY=true
    echo "Desktop window is ready."
    break
  fi

  sleep 1
done

if [[ "${WINDOW_READY}" != "true" ]]; then
  echo "WARNING: desktop window readiness check timed out."
fi

sleep 3

echo "===== Running Desktop Observer ====="
cd /root/workspace

python3 -m desktop.observer \
  >/tmp/desktop-observer.log 2>&1 || true

echo "===== Running Desktop Controller Demo ====="
python3 -m desktop.controller \
  >/tmp/desktop-controller.log 2>&1 || true

echo "===== Running Desktop Tools Demo ====="
python3 -m desktop.tools \
  >/tmp/desktop-tools.log 2>&1 || true

echo "===== Generated Artifacts ====="
ls -lh /root/artifacts || true

echo "===== Desktop Observer log ====="
tail -100 /tmp/desktop-observer.log || true

echo "===== Desktop Controller log ====="
tail -100 /tmp/desktop-controller.log || true

echo "===== Desktop Tools log ====="
tail -100 /tmp/desktop-tools.log || true

echo "===== Processes ====="
ps -ef \
  | grep -E 'ttyd|Xvfb|x0vncserver|code-server|firefox|websockify' \
  | grep -v grep \
  || true

echo "===== Starting noVNC ====="
cd /opt/novnc

exec ./utils/novnc_proxy \
  --listen 6080 \
  --vnc localhost:5900