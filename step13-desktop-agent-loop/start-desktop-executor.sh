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

echo "===== STEP12 Desktop Executor ====="
date

echo "===== Versions ====="
python3 --version
node --version
npm --version
git --version
claude --version || true
code-server --version || true

echo "===== Configure Desktop Executor ====="
python3 /root/configure-desktop-executor.py

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

echo "===== Starting Firefox ====="

firefox \
    --no-remote \
    --new-window \
    http://127.0.0.1:8081 \
    >/tmp/firefox.log 2>&1 &

echo "Waiting for Firefox..."

for _ in $(seq 1 60); do
    if xlsclients 2>/dev/null | grep firefox >/dev/null; then
        echo "Firefox is ready."
        break
    fi
    sleep 1
done

sleep 3

echo "===== Desktop Observer ====="
python3 -m desktop.observer \
    >/tmp/desktop-observer.log 2>&1 || true

echo "===== Desktop Controller ====="
python3 -m desktop.controller \
    >/tmp/desktop-controller.log 2>&1 || true

echo "===== Desktop Tools ====="
python3 -m desktop.tools \
    >/tmp/desktop-tools.log 2>&1 || true

echo "===== Desktop Executor ====="
echo "Executor is ready but will not run automatically."
echo
echo "Safe first test:"
echo "  python3 -m desktop.executor"
echo
echo "Action queue:"
echo "  /root/artifacts/desktop-actions.json"
echo
echo "Execution result:"
echo "  /root/artifacts/desktop-execution.json"
echo
echo "===== Executor ====="

if [[ -f /tmp/desktop-executor.log ]]; then
    tail -100 /tmp/desktop-executor.log
else
    echo "Executor has not been run yet."
fi

echo "===== Generated Artifacts ====="

ls -lh /root/artifacts || true

echo
echo "===== Observer ====="
tail -100 /tmp/desktop-observer.log || true

echo
echo "===== Controller ====="
tail -100 /tmp/desktop-controller.log || true

echo
echo "===== Tools ====="
tail -100 /tmp/desktop-tools.log || true

echo
echo "===== Executor ====="
tail -100 /tmp/desktop-executor.log || true

echo
echo "===== Running Processes ====="

ps -ef |
grep -E 'ttyd|Xvfb|x0vncserver|code-server|firefox|websockify' |
grep -v grep || true

echo
echo "===== Starting noVNC ====="

cd /opt/novnc

exec ./utils/novnc_proxy \
    --listen 6080 \
    --vnc localhost:5900