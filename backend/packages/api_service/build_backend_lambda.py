import os
from pathlib import Path
import shutil
import subprocess


BUILD_DIRECTORY = Path(__file__).parent / "lambda_build"
DOCKERFILE = Path(__file__).parent / "Dockerfile.lambda"
IMAGE_NAME = "lambda-build"


def clean_build_directory() -> None:
    shutil.rmtree(BUILD_DIRECTORY, ignore_errors=True)
    os.mkdir(BUILD_DIRECTORY)


def run_docker_build() -> None:
    command = [
        "docker",
        "buildx",
        "build",
        "-f",
        str(DOCKERFILE),
        "--tag",
        IMAGE_NAME,
        "--platform",
        "linux/arm64",
        str(DOCKERFILE.parent),
    ]

    print("Building image for deployment environment...")
    subprocess.run(command, check=True)


def build_lambda_zip() -> None:
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{BUILD_DIRECTORY}:/mnt/result",
        "--platform",
        "linux/arm64",
        IMAGE_NAME,
    ]

    print("Running build image to create Lambda build zip...")
    subprocess.run(command, check=True)


def main() -> None:
    clean_build_directory()
    run_docker_build()
    build_lambda_zip()


if __name__ == "__main__":
    main()
