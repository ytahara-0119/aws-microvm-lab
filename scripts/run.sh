#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <step>"
    exit 1
fi

STEP="$1"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROOT_DIR

CONFIG="${ROOT_DIR}/scripts/config/${STEP}.env"

if [[ ! -f "$CONFIG" ]]; then
    echo "Config not found: $CONFIG"
    exit 1
fi

source "$CONFIG"
source "${ROOT_DIR}/scripts/common/run-microvm.sh"
