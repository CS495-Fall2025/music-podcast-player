import asyncio
import os
import secrets
import socket
from uuid import uuid4

from lnbits import wallets
from lnbits.core import services, models, helpers
from lnbits.core.models import extensions as ex_models


def main() -> None:
    print("Setting up databases")
    asyncio.run(helpers.migrate_databases())

    print("Migrating extensions")
    extension = ex_models.InstallableExtension(id="nwcprovider", name="nwcprovider", version="1.0.0")
    asyncio.run(helpers.migrate_extension_database(extension))

    print("Initializing NWC Provider")
    initialize_nwcprovider()


def initialize_nwcprovider() -> None:
    from lnbits.extensions import nwcprovider as nwc

    secret = secrets.token_hex(32)
    lan_ip = socket.gethostbyname("host-lan")
    relay_url = f"ws://{lan_ip}:8080"

    asyncio.run(nwc.crud.set_config_nwc("relay", relay_url))
    asyncio.run(nwc.crud.set_config_nwc("provider_key", secret))


if __name__ == "__main__":
    main()
