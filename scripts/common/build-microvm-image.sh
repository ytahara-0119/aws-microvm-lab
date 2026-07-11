#!/usr/bin/env bash
set -euo pipefail

: "${ROOT_DIR:?ROOT_DIR is required}"
: "${STEP_DIR:?STEP_DIR is required}"
: "${IMAGE_NAME:?IMAGE_NAME is required}"
: "${ZIP_NAME:?ZIP_NAME is required}"
: "${REGION:?REGION is required}"
: "${ACCOUNT_ID:?ACCOUNT_ID is required}"
: "${BUCKET_NAME:?BUCKET_NAME is required}"
: "${BUILD_ROLE_ARN:?BUILD_ROLE_ARN is required}"

STEP_PATH="${ROOT_DIR}/${STEP_DIR}"
ZIP_PATH="${STEP_PATH}/app.zip"
S3_KEY="${ZIP_NAME}"

echo
echo "========================================"
echo "Build MicroVM Image"
echo "========================================"
echo "Step dir : ${STEP_DIR}"
echo "Image    : ${IMAGE_NAME}"
echo "Zip      : ${S3_KEY}"
echo

cd "${STEP_PATH}"

rm -f app.zip

zip -r app.zip \
    . \
    -x "app.zip" \
    -x "*/__pycache__/*" \
    -x "*.pyc" \
    -x "*.DS_Store"

echo
echo "ZIP contents:"
unzip -l app.zip

echo
echo "Uploading to S3..."
aws s3 cp \
    "${ZIP_PATH}" \
    "s3://${BUCKET_NAME}/${S3_KEY}"

echo
echo "Creating MicroVM image..."
aws lambda-microvms create-microvm-image \
    --name "${IMAGE_NAME}" \
    --code-artifact uri="s3://${BUCKET_NAME}/${S3_KEY}" \
    --base-image-arn "arn:aws:lambda:${REGION}:aws:microvm-image:al2023-1" \
    --build-role-arn "${BUILD_ROLE_ARN}" \
    --region "${REGION}"

echo
echo "========================================"
echo "Next Commands"
echo "========================================"

echo
echo "Check image:"
echo "aws lambda-microvms get-microvm-image \\"
echo "  --image-identifier arn:aws:lambda:${REGION}:${ACCOUNT_ID}:microvm-image:${IMAGE_NAME} \\"
echo "  --region ${REGION}"

echo
echo "If CREATE_FAILED, check build logs:"
echo "aws logs tail \\"
echo "  /aws/lambda-microvms/${IMAGE_NAME} \\"
echo "  --since 30m \\"
echo "  --region ${REGION}"

echo
echo "If build succeeded:"
echo "./scripts/run.sh ${STEP}"