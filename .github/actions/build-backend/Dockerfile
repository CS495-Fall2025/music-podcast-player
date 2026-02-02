FROM --platform=linux/arm64 public.ecr.aws/amazonlinux/amazonlinux:2023

# For future modifications resulting from changing Dockerfile.lambda:
# This and entrypoint are effectively a duplicate of Dockerfile.lambda, except the repo
# is in a volume /github/workspace/backend. Additionally, the build is output to
# /github/workspace/build/backend-build.zip

# Install general dependencies
RUN dnf install -y python312
RUN python3.12 -m ensurepip --upgrade

# Install dependencies for psycogp2
RUN dnf install -y python3.12-devel postgresql-devel gcc make

COPY entrypoint.sh ./
RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
