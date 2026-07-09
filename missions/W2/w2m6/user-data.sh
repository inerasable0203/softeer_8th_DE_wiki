#!/bin/bash
set -euxo pipefail

exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# Fill these values after creating your ECR repository.
AWS_REGION="ap-northeast-2"
AWS_ACCOUNT_ID="118094646679"
ECR_REPOSITORY="inerasable0203/w2m6"
IMAGE_TAG="latest"

CONTAINER_NAME="w2m6-jupyterlab"
HOST_PORT="8888"
JUPYTER_TOKEN="w2m6-token"

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

install_docker_and_aws_cli() {
  if command -v dnf >/dev/null 2>&1; then
    dnf update -y
    dnf install -y docker awscli
  elif command -v yum >/dev/null 2>&1; then
    yum update -y
    yum install -y docker awscli
  elif command -v apt-get >/dev/null 2>&1; then
    apt-get update -y
    apt-get install -y docker.io awscli
  else
    echo "No supported package manager found." >&2
    exit 1
  fi
}

install_docker_and_aws_cli

systemctl enable docker
systemctl start docker

if id ec2-user >/dev/null 2>&1; then
  usermod -aG docker ec2-user
fi

if id ubuntu >/dev/null 2>&1; then
  usermod -aG docker ubuntu
fi

aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

docker pull "${IMAGE_URI}"
docker rm -f "${CONTAINER_NAME}" || true
docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -p "${HOST_PORT}:8888" \
  -e JUPYTER_TOKEN="${JUPYTER_TOKEN}" \
  "${IMAGE_URI}"

docker ps
