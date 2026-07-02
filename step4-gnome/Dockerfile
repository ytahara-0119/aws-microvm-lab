FROM public.ecr.aws/lambda/microvms:al2023-minimal

RUN dnf install -y \
    bash \
    procps-ng \
    iproute \
    util-linux \
    vim-minimal \
    less \
    which \
    tar \
    gzip \
    python3 \
    xorg-x11-server-Xvfb \
    xterm \
    tigervnc-server \
    gnome-session \
    gnome-session-xsession \
    gnome-shell \
    gnome-settings-daemon \
    gnome-classic-session \
 && dnf clean all

RUN /usr/bin/curl -L \
  https://github.com/novnc/noVNC/archive/refs/tags/v1.5.0.tar.gz \
  -o /tmp/novnc.tar.gz \
 && mkdir -p /opt/novnc \
 && tar -xzf /tmp/novnc.tar.gz -C /opt/novnc --strip-components=1 \
 && rm -f /tmp/novnc.tar.gz

RUN /usr/bin/curl -L \
  https://github.com/novnc/websockify/archive/refs/tags/v0.12.0.tar.gz \
  -o /tmp/websockify.tar.gz \
 && mkdir -p /opt/novnc/utils/websockify \
 && tar -xzf /tmp/websockify.tar.gz -C /opt/novnc/utils/websockify --strip-components=1 \
 && rm -f /tmp/websockify.tar.gz

RUN cat > /usr/local/bin/start-novnc.sh <<'EOS'
#!/usr/bin/env bash
set -x

exec > >(tee -a /tmp/start.log) 2>&1

echo "===== start-novnc.sh started ====="
date
whoami
pwd
env | sort

export DISPLAY=:1
export XDG_SESSION_TYPE=x11
export GNOME_SHELL_SESSION_MODE=classic
export NO_AT_BRIDGE=1

echo "===== checking commands ====="
which Xvfb || true
which xterm || true
which x0vncserver || true
which vncpasswd || true
which dbus-run-session || true
which gnome-session || true
which gnome-shell || true

echo "===== starting Xvfb ====="
Xvfb :1 -screen 0 1280x720x24 &
XVFB_PID=$!
echo "Xvfb PID=${XVFB_PID}"
sleep 2

echo "===== setting VNC password ====="
mkdir -p /root/.vnc
printf "microvm\nmicrovm\nn\n" | vncpasswd

echo "===== starting TigerVNC x0vncserver ====="
x0vncserver \
  -display :1 \
  -rfbport 5900 \
  -PasswordFile /root/.vnc/passwd \
  -SecurityTypes VncAuth &
VNC_PID=$!
echo "x0vncserver PID=${VNC_PID}"
sleep 2

echo "===== starting debug xterm only ====="
xterm -geometry 120x35+20+20 \
  -title "MicroVM Debug" \
  -e "echo 'MicroVM Debug Shell'; echo; echo 'Try:'; echo '  cat /tmp/start.log'; echo '  dbus-run-session -- gnome-session --session=gnome-classic > /tmp/gnome-session.log 2>&1'; echo '  cat /tmp/gnome-session.log'; echo; bash" &
XTERM_PID=$!
echo "xterm PID=${XTERM_PID}"
sleep 2

echo "===== process snapshot ====="
ps aux | grep -E 'Xvfb|xterm|vnc|gnome|dbus' || true

echo "===== start.log tail ====="
tail -100 /tmp/start.log || true

echo "===== starting noVNC ====="
cd /opt/novnc
exec ./utils/novnc_proxy --vnc localhost:5900 --listen 6080
EOS

RUN chmod +x /usr/local/bin/start-novnc.sh

EXPOSE 6080

CMD ["/usr/local/bin/start-novnc.sh"]
