#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <step>"
  echo "Example:"
  echo "  ./scripts/run.sh step11"
  exit 1
fi

STEP="$1"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROOT_DIR

CONFIG_DIR="${ROOT_DIR}/scripts/config"
COMMON_CONFIG="${CONFIG_DIR}/common.env"
STEP_CONFIG="${CONFIG_DIR}/${STEP}.env"

if [[ ! -f "${COMMON_CONFIG}" ]]; then
  echo "Common config not found: ${COMMON_CONFIG}"
  exit 1
fi

if [[ ! -f "${STEP_CONFIG}" ]]; then
  echo "Step config not found: ${STEP_CONFIG}"
  exit 1
fi

source "${COMMON_CONFIG}"
source "${STEP_CONFIG}"

: "${STEP_DIR:?STEP_DIR is required}"
: "${IMAGE_VERSION:?IMAGE_VERSION is required}"

if [[ "${STEP_DIR}" =~ ^step[0-9]+-(.+)$ ]]; then
  STEP_NAME="${BASH_REMATCH[1]}"
else
  echo "Invalid STEP_DIR format: ${STEP_DIR}"
  echo "Expected format: step<number>-<name>"
  exit 1
fi

VERSION_MAJOR="${IMAGE_VERSION%%.*}"
IMAGE_NAME="${STEP_NAME}-v${VERSION_MAJOR}"
ZIP_NAME="${STEP_DIR}-v${VERSION_MAJOR}.zip"

export STEP_NAME
export VERSION_MAJOR
export IMAGE_NAME
export ZIP_NAME

echo
echo "========================================"
echo "Resolved Run Configuration"
echo "========================================"
echo "Step                  : ${STEP}"
echo "Step dir              : ${STEP_DIR}"
echo "Image name            : ${IMAGE_NAME}"
echo "AWS image version     : ${MICROVM_IMAGE_VERSION:-1.0}"
echo "Target port           : ${TARGET_PORT}"
echo

source "${ROOT_DIR}/scripts/common/run-microvm.sh"