import os
from pathlib import Path
import socket
import subprocess


COMPOSE_DIRECTORY = Path(__file__).parent


def main() -> None:
    env = os.environ.copy()

    if "HOST_LAN_IP" not in env:
        env["HOST_LAN_IP"] = get_lan_ip()

    print(
        "You can connect to each Alby wallet here:\n"
        f"- Listener: http://{env["HOST_LAN_IP"]}:4000\n"
        f"- Artist: http://{env["HOST_LAN_IP"]}:4001"
    )

    start_test_environment(env)


def get_lan_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
        except Exception:
            ip = "localhost"

    return ip


def start_test_environment(env: dict[str, str]) -> None:
    try:
        subprocess.run(
            ["docker", "compose", "down", "-v"],
            cwd=COMPOSE_DIRECTORY,
            env=env
        )
        subprocess.run(
            ["docker", "compose", "up"],
            cwd=COMPOSE_DIRECTORY,
            env=env
        )
    except KeyboardInterrupt:
        print("Stopping...")


if __name__ == "__main__":
    main()
