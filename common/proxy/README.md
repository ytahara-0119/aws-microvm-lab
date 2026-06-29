# MicroVM Proxy

Local HTTP/WebSocket proxy for AWS Lambda MicroVM endpoints.

## Purpose

AWS Lambda MicroVM endpoints require special headers:

- `X-aws-proxy-auth`
- `X-aws-proxy-port`

Browsers cannot easily add these headers by themselves.

This proxy runs on localhost and forwards requests to the MicroVM endpoint with the required headers.

It also supports WebSocket forwarding for tools such as:

- ttyd
- noVNC
- code-server

## Install

```bash
cd common/proxy
uv sync
Environment variables
export MICROVM_ID=<microvm-id>
export ENDPOINT=<microvm-endpoint>
export TARGET_PORT=7681

Create auth token:

export TOKEN=$(aws lambda-microvms create-microvm-auth-token \
  --microvm-identifier "$MICROVM_ID" \
  --expiration-in-minutes 30 \
  --allowed-ports "[{\"port\":${TARGET_PORT}}]" \
  --region ap-northeast-1 \
  --query 'authToken."X-aws-proxy-auth"' \
  --output text)
Run
uv run microvm-proxy

Open:

http://localhost:8080
Optional settings
export LISTEN_HOST=127.0.0.1
export LISTEN_PORT=8080

