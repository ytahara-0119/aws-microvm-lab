FROM public.ecr.aws/lambda/microvms:al2023-minimal

RUN dnf install -y \
    bash \
    python3 \
    python3-pip \
    git \
    nodejs \
    npm \
    procps-ng \
    util-linux \
    less \
    which \
    tar \
    gzip \
    git \
    glibc-langpack-ja \
    google-noto-sans-cjk-fonts \
    google-noto-emoji-fonts \
    xorg-x11-server-Xvfb \
    tigervnc-server \
    firefox \
    xwininfo \
    xlsclients \
    xdpyinfo \
    xrandr \
    xset \
    xsetroot \
    ImageMagick \
 && dnf clean all

ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=Asia/Tokyo

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
 && echo "Asia/Tokyo" > /etc/timezone

RUN /usr/bin/curl -L \
  https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.aarch64 \
  -o /usr/local/bin/ttyd \
 && chmod +x /usr/local/bin/ttyd

RUN /usr/bin/curl -L \
  https://github.com/novnc/noVNC/archive/refs/tags/v1.5.0.tar.gz \
  -o /tmp/novnc.tar.gz \
 && mkdir -p /opt/novnc \
 && tar -xzf /tmp/novnc.tar.gz -C /opt/novnc --strip-components=1 \
 && rm /tmp/novnc.tar.gz

RUN /usr/bin/curl -L \
  https://github.com/novnc/websockify/archive/refs/tags/v0.12.0.tar.gz \
  -o /tmp/websockify.tar.gz \
 && mkdir -p /opt/novnc/utils/websockify \
 && tar -xzf /tmp/websockify.tar.gz -C /opt/novnc/utils/websockify --strip-components=1 \
 && rm /tmp/websockify.tar.gz

RUN /usr/bin/curl -fsSL \
  https://code-server.dev/install.sh \
  | sh

RUN npm install -g @anthropic-ai/claude-code

RUN python3 --version \
 && node --version \
 && npm --version \
 && claude --version

COPY start-desktop-agent.sh /usr/local/bin/
COPY configure-desktop-agent.py /root/configure-desktop-agent.py
COPY desktop_observer.py /root/workspace/desktop_observer.py
COPY desktop_controller.py /root/workspace/desktop_controller.py

RUN chmod +x /usr/local/bin/start-desktop-agent.sh

EXPOSE 6080
EXPOSE 7681
EXPOSE 8081

CMD ["/usr/local/bin/start-desktop-agent.sh"]
