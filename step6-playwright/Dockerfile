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
    glibc-langpack-ja \
    google-noto-sans-cjk-fonts \
    google-noto-emoji-fonts \
    xorg-x11-server-Xvfb \
    tigervnc-server \
    firefox \
 && dnf clean all

RUN /usr/bin/curl -L \
  https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.aarch64 \
  -o /usr/local/bin/ttyd \
 && chmod +x /usr/local/bin/ttyd

ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=Asia/Tokyo
ENV PLAYWRIGHT_BROWSERS_PATH=0

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
 && echo "Asia/Tokyo" > /etc/timezone

RUN pip3 install --no-cache-dir playwright
RUN python3 -m playwright install firefox

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

COPY start-playwright.sh /usr/local/bin/
COPY demo_playwright.py /root/demo_playwright.py

RUN chmod +x /usr/local/bin/start-playwright.sh

EXPOSE 6080

CMD ["/usr/local/bin/start-playwright.sh"]
