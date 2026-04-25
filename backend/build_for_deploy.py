import os
from pathlib import Path
import platform
import shutil
import subprocess

BUILD_DIR = Path(__file__).parent / "builds"
IMAGES_DIR = Path(__file__).parent / "docker" / "lambda"

PACKAGE_NAMES = [
    "api-service",
    "db-service",
    "migration-handler",
    "page-initializer",
    "make-admin",
]


def install_arm_emulation() -> bool:
    if platform.machine() == "aarch64":
        print("Host machine architecture is ARM64, skipping emulation.")
        return False

    print("Enabling ARM emulation.")
    subprocess.run(
        [
            "docker",
            "run",
            "--privileged",
            "--rm",
            "tonistiigi/binfmt",
            "--install",
            "arm64",
        ],
        check=True,
    )

    return True


def clean_build_directory() -> None:
    print("Cleaning build directory.")
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    os.mkdir(BUILD_DIR)


def build_package(name: str, emulation: bool) -> None:
    image_build_command = [
        "docker",
        "buildx",
        "build",
        "-f",
        str(IMAGES_DIR / f"Dockerfile.{name}"),
        "--tag",
        f"rss-music-{name}",
    ]

    if emulation:
        image_build_command += ["--platform", "linux/arm64"]

    image_build_command += ["."]

    print(f"Building build image for {name}")
    subprocess.run(image_build_command, check=True)

    run_command = ["docker", "run", "--rm", "-v", f"{BUILD_DIR}:/mnt/result"]

    if emulation:
        run_command += ["--platform", "linux/arm64"]

    run_command += [f"rss-music-{name}"]

    print(f"Packaging {name}")
    subprocess.run(run_command, check=True)


def main() -> None:
    emulation = install_arm_emulation()
    clean_build_directory()
    for package in PACKAGE_NAMES:
        build_package(package, emulation)


if __name__ == "__main__":
    main()
