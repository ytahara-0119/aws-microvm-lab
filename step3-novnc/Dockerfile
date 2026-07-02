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
set -e

export DISPLAY=:1

Xvfb :1 -screen 0 1280x720x24 &
sleep 1

xterm -geometry 100x30+20+20 &

mkdir -p /root/.vnc
printf "microvm\nmicrovm\nn\n" | vncpasswd

x0vncserver \
  -display :1 \
  -rfbport 5900 \
  -PasswordFile /root/.vnc/passwd \
  -SecurityTypes VncAuth &

cd /opt/novnc
exec ./utils/novnc_proxy --vnc localhost:5900 --listen 6080
EOS

RUN chmod +x /usr/local/bin/start-novnc.sh

EXPOSE 6080

CMD ["/usr/local/bin/start-novnc.sh"]
