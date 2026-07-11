#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-ap-northeast-1}"
MICROVM_IMAGE_VERSION="${MICROVM_IMAGE_VERSION:-1.0}"
LOCAL_PORT="${LOCAL_PORT:-8080}"

: "${IMAGE_NAME:?IMAGE_NAME is required}"
: "${TARGET_PORT:?TARGET_PORT is required}"
: "${URL:?URL is required}"
: "${ROOT_DIR:?ROOT_DIR is required}"

ACCOUNT_ID=$(aws sts get-caller-identity \
  --query Account \
  --output text)

EXEC_ROLE_ARN=$(aws iam get-role \
  --role-name MicroVMExecutionRole \
  --query Role.Arn \
  --output text)

echo
echo "========================================"
echo "Starting MicroVM"
echo "========================================"
echo "Image : ${IMAGE_NAME}"
echo "Port  : ${TARGET_PORT}"
echo

RUN_RESULT=$(aws lambda-microvms run-microvm \
  --image-identifier "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:microvm-image:${IMAGE_NAME}" \
  --image-version "${MICROVM_IMAGE_VERSION}" \
  --execution-role-arn "${EXEC_ROLE_ARN}" \
  --idle-policy maxIdleDurationSeconds=900,suspendedDurationSeconds=1800,autoResumeEnabled=true \
  --region "${REGION}")

MICROVM_ID=$(echo "${RUN_RESULT}" | jq -r '.microvmId')
ENDPOINT=$(echo "${RUN_RESULT}" | jq -r '.endpoint')

if [[ -n "${TERMINAL_PORT:-}" && -n "${VNC_PORT:-}" ]]; then
  ALLOWED_PORTS_JSON=$(jq -nc \
    --argjson vnc "${VNC_PORT}" \
    --argjson terminal "${TERMINAL_PORT}" \
    '[{"port":$vnc},{"port":$terminal}]')
else
  ALLOWED_PORTS_JSON=$(jq -nc \
    --argjson port "${TARGET_PORT}" \
    '[{"port":$port}]')
fi

echo "Allowed ports: ${ALLOWED_PORTS_JSON}"

TOKEN=$(aws lambda-microvms create-microvm-auth-token \
  --microvm-identifier "${MICROVM_ID}" \
  --expiration-in-minutes 60 \
  --allowed-ports "${ALLOWED_PORTS_JSON}" \
  --region "${REGION}" \
  --query 'authToken."X-aws-proxy-auth"' \
  --output text)

export MICROVM_ID
export ENDPOINT
export TOKEN
export TARGET_PORT
export VNC_PORT="${VNC_PORT:-6080}"
export TERMINAL_PORT="${TERMINAL_PORT:-7681}"
export LISTEN_PORT="${LOCAL_PORT}"

echo
echo "MicroVM ID : ${MICROVM_ID}"
echo "Endpoint   : ${ENDPOINT}"
echo "Target port: ${TARGET_PORT}"
echo
echo "Open:"
echo "  http://localhost:${LOCAL_PORT}${URL}"
echo
echo "Proxy starting..."
echo "Press Ctrl+C to stop proxy."
echo

cd "${ROOT_DIR}/common/proxy"
uv run microvm-proxy
