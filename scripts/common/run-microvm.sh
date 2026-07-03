#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-ap-northeast-1}"
IMAGE_VERSION="${IMAGE_VERSION:-1.0}"
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
  --image-version "${IMAGE_VERSION}" \
  --execution-role-arn "${EXEC_ROLE_ARN}" \
  --idle-policy maxIdleDurationSeconds=900,suspendedDurationSeconds=1800,autoResumeEnabled=true \
  --region "${REGION}")

MICROVM_ID=$(echo "${RUN_RESULT}" | jq -r '.microvmId')
ENDPOINT=$(echo "${RUN_RESULT}" | jq -r '.endpoint')

TOKEN=$(aws lambda-microvms create-microvm-auth-token \
  --microvm-identifier "${MICROVM_ID}" \
  --expiration-in-minutes 60 \
  --allowed-ports "[{\"port\":${TARGET_PORT}}]" \
  --region "${REGION}" \
  --query 'authToken."X-aws-proxy-auth"' \
  --output text)

export MICROVM_ID
export ENDPOINT
export TOKEN
export TARGET_PORT
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
