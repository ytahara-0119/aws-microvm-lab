#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-ap-northeast-1}"
IMAGE_NAME="${IMAGE_NAME:-terminal-microvm-demo-v3}"
IMAGE_VERSION="${IMAGE_VERSION:-1.0}"
TARGET_PORT="${TARGET_PORT:-7681}"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

EXEC_ROLE_ARN=$(aws iam get-role \
  --role-name MicroVMExecutionRole \
  --query Role.Arn \
  --output text)

echo "Starting MicroVM image: ${IMAGE_NAME}"

RUN_RESULT=$(aws lambda-microvms run-microvm \
  --image-identifier "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:microvm-image:${IMAGE_NAME}" \
  --image-version "${IMAGE_VERSION}" \
  --execution-role-arn "${EXEC_ROLE_ARN}" \
  --idle-policy maxIdleDurationSeconds=900,suspendedDurationSeconds=1800,autoResumeEnabled=true \
  --region "${REGION}")

MICROVM_ID=$(echo "$RUN_RESULT" | python3 -c 'import sys,json; print(json.load(sys.stdin)["microvmId"])')
ENDPOINT=$(echo "$RUN_RESULT" | python3 -c 'import sys,json; print(json.load(sys.stdin)["endpoint"])')

echo "MICROVM_ID=${MICROVM_ID}"
echo "ENDPOINT=${ENDPOINT}"

TOKEN=$(aws lambda-microvms create-microvm-auth-token \
  --microvm-identifier "$MICROVM_ID" \
  --expiration-in-minutes 60 \
  --allowed-ports "[{\"port\":${TARGET_PORT}}]" \
  --region "${REGION}" \
  --query 'authToken."X-aws-proxy-auth"' \
  --output text)

export MICROVM_ID
export ENDPOINT
export TOKEN
export TARGET_PORT

echo
echo "Open:"
echo "  http://localhost:8080/"
echo
echo "Target port:"
echo "  ${TARGET_PORT}"
echo

cd "$(dirname "$0")/../common/proxy"
exec uv run microvm-proxy
