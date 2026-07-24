# --------------------------------------------------------------------
# STEP18 ParrotOS Desktop (sub-project)
#
# 既存STEP(1〜17)は全て
#   FROM public.ecr.aws/lambda/microvms:al2023-minimal
# だが、本物のParrotOS(Debianベース)を動かすため、ここだけ
# ParrotSec公式イメージを直接FROMにする。
#
# scripts/common/build-microvm-image.sh は全STEP共通で
#   --base-image-arn arn:aws:lambda:<region>:aws:microvm-image:al2023-1
# を固定指定しているが、実機で本イメージのビルド・起動が
# 確認できている(FROMの違いは問題にならない)。
# --------------------------------------------------------------------

FROM parrotsec/core:latest

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    GEOMETRY=1280x800 \
    VNC_PORT=6080 \
    RFB_PORT=5900 \
    HOOK_PORT=9000 \
    LANG=ja_JP.UTF-8 \
    LC_ALL=ja_JP.UTF-8 \
    TZ=Asia/Tokyo

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      dbus-x11 \
      firefox-esr \
      fonts-noto-cjk \
      locales \
      procps \
      python3 \
      tini \
      tzdata \
      x11-utils \
      x11-xserver-utils \
      x11vnc \
      xfce4 \
      xfce4-terminal \
      xfce4-whiskermenu-plugin \
      xvfb \
    && sed -i 's/^# *\(ja_JP.UTF-8 UTF-8\)/\1/' /etc/locale.gen \
    && locale-gen \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && echo "Asia/Tokyo" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# noVNC + websockify
# (他STEPと同じくコンテナ内にバンドルし、6080番でHTTP配信する。
#  これによりcommon/proxy経由でブラウザから /vnc.html にアクセスできる)
RUN curl -L \
      https://github.com/novnc/noVNC/archive/refs/tags/v1.5.0.tar.gz \
      -o /tmp/novnc.tar.gz \
    && mkdir -p /opt/novnc \
    && tar -xzf /tmp/novnc.tar.gz -C /opt/novnc --strip-components=1 \
    && rm -f /tmp/novnc.tar.gz

RUN curl -L \
      https://github.com/novnc/websockify/archive/refs/tags/v0.12.0.tar.gz \
      -o /tmp/websockify.tar.gz \
    && mkdir -p /opt/novnc/utils/websockify \
    && tar -xzf /tmp/websockify.tar.gz -C /opt/novnc/utils/websockify --strip-components=1 \
    && rm -f /tmp/websockify.tar.gz

COPY start-parrotos-desktop.sh /usr/local/bin/start-parrotos-desktop.sh
COPY hooks_server.py /opt/microvm/hooks_server.py

RUN chmod +x /usr/local/bin/start-parrotos-desktop.sh

# 6080: noVNC (ブラウザからアクセスする想定のポート)
# 9000: MicroVMライフサイクルフック(AL2023ベースイメージには
#       標準搭載されている想定のフックを、非AL2023ベースのため
#       自前で実装している。詳細はhooks_server.py参照)
EXPOSE 6080 9000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/local/bin/start-parrotos-desktop.sh"]
