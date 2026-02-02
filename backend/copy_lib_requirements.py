from pathlib import Path

import shutil
import subprocess


OUTPUT_PATH = Path(__file__).parent / "lib"
PACKAGES_PATH = Path(__file__).parent


DEPENDEE_OBJECTS = [
    PACKAGES_PATH / "psycopg2" / "_psycopg*.so",
]


SYSTEM_LIBRARIES = [
    "libc",
    "libpthread",
    "libdl",
    "libm",
    "libresolv",
    "libcrypt",
    "libselinux",
    "librt",
    "libkeyutils",
    "ld-linux",
]


def get_dependencies() -> list[str]:
    cmd = "ldd {dependee} | awk '{{print $3}}' | grep '^/'"

    dependencies = set()
    for dependee in DEPENDEE_OBJECTS:
        result = subprocess.run(
            cmd.format(dependee=dependee),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for dependency in result.stdout.strip().splitlines():
            dependencies.add(dependency)

    to_remove = []
    for dependency in dependencies:
        for sys_lib in SYSTEM_LIBRARIES:
            if sys_lib in dependency:
                to_remove.append(dependency)
                break

    for dependency in to_remove:
        dependencies.remove(dependency)

    return list(dependencies)


def copy_dependencies(dependencies: list[str]) -> None:
    for dependency in dependencies:
        shutil.copy(dependency, OUTPUT_PATH)


def main() -> None:
    dependencies = get_dependencies()
    copy_dependencies(dependencies)


if __name__ == "__main__":
    main()
