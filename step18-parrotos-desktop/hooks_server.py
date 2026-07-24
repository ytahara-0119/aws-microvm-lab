#!/usr/bin/env python3
"""AWS Lambda MicroVM lifecycle hook server.

既存STEP(1〜15)は public.ecr.aws/lambda/microvms:al2023-minimal を
ベースにしており、MicroVMのライフサイクルフック(ready/validate/run/
resume/suspend/terminate)はそのベースイメージ側で処理されている
(と推測される)。

このSTEPだけ本物のParrotOS(非AL2023ベース)を使うため、フックを
自前で実装する必要がある。実装は以下を参考にした:
  https://github.com/Kanahiro/microvm-desktop
  (microvm-image/hooks_server.py, MIT License相当の構成を踏襲)

未検証事項:
  scripts/common/build-microvm-image.sh は全STEP共通で
  --base-image-arn arn:aws:lambda:<region>:aws:microvm-image:al2023-1
  を固定指定しているため、このフック実装が実際にAWS Lambda MicroVMs
  側から呼び出されるかどうかは未確認。ビルド・起動時にエラーが出る
  場合はbuild-microvm-image.shのbase-image-arn指定を見直すこと。
"""
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = "/aws/lambda-microvms/runtime/v1"
PORT = int(os.getenv("HOOK_PORT", "9000"))
# ready判定は「ブラウザから使える状態か」を意味するnoVNCのHTTPポートを見る
READY_CHECK_PORT = int(os.getenv("VNC_PORT", "6080"))


def desktop_ready() -> bool:
    with socket.socket() as connection:
        connection.settimeout(0.2)
        return connection.connect_ex(("127.0.0.1", READY_CHECK_PORT)) == 0


class Handler(BaseHTTPRequestHandler):
    def handle_hook(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)

        hook = self.path.split("?", 1)[0].removeprefix(f"{BASE}/")

        if hook == "ready":
            status = 200 if desktop_ready() else 503
        elif hook in {"validate", "run", "resume", "suspend", "terminate"}:
            status = 200
        else:
            status = 404

        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_GET = handle_hook
    do_POST = handle_hook

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
