FROM public.ecr.aws/lambda/microvms:al2023-minimal

RUN dnf install -y \
    bash \
    python3 \
    python3-pip \
    procps-ng \
    util-linux \
    less \
    which \
    tar \
    gzip \
    git \
    nodejs \
    npm \
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
ENV DISPLAY=:1
ENV HOME=/root
ENV PYTHONPATH=/root/workspace

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
 && echo "Asia/Tokyo" > /etc/timezone

# ttyd
RUN /usr/bin/curl -L \
  https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.aarch64 \
  -o /usr/local/bin/ttyd \
 && chmod +x /usr/local/bin/ttyd

# noVNC
RUN /usr/bin/curl -L \
  https://github.com/novnc/noVNC/archive/refs/tags/v1.5.0.tar.gz \
  -o /tmp/novnc.tar.gz \
 && mkdir -p /opt/novnc \
 && tar -xzf /tmp/novnc.tar.gz \
      -C /opt/novnc \
      --strip-components=1 \
 && rm -f /tmp/novnc.tar.gz

# websockify
RUN /usr/bin/curl -L \
  https://github.com/novnc/websockify/archive/refs/tags/v0.12.0.tar.gz \
  -o /tmp/websockify.tar.gz \
 && mkdir -p /opt/novnc/utils/websockify \
 && tar -xzf /tmp/websockify.tar.gz \
      -C /opt/novnc/utils/websockify \
      --strip-components=1 \
 && rm -f /tmp/websockify.tar.gz

# code-server
RUN /usr/bin/curl -fsSL \
  https://code-server.dev/install.sh \
  | sh

# Claude Code
RUN npm install -g @anthropic-ai/claude-code

# ビルド時のバージョン確認
RUN python3 --version \
 && node --version \
 && npm --version \
 && git --version \
 && code-server --version \
 && claude --version

RUN mkdir -p \
    /root/workspace \
    /root/artifacts

COPY configure-desktop-tools.py \
  /root/configure-desktop-tools.py

COPY start-desktop-tools.sh \
  /usr/local/bin/start-desktop-tools.sh

COPY desktop \
  /root/workspace/desktop

RUN chmod +x /usr/local/bin/start-desktop-tools.sh

EXPOSE 6080
EXPOSE 7681
EXPOSE 8081

CMD ["/usr/local/bin/start-desktop-tools.sh"]