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
 && dnf clean all

RUN /usr/bin/curl -L \
  https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.aarch64 \
  -o /usr/local/bin/ttyd \
 && chmod +x /usr/local/bin/ttyd \
 && /usr/local/bin/ttyd --version

EXPOSE 7681

WORKDIR /root

CMD ["/usr/local/bin/ttyd", "-p", "7681", "-i", "0.0.0.0", "-W", "bash"]
