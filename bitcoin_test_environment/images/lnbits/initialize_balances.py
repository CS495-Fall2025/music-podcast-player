import asyncio
import os
from uuid import uuid4

from lnbits import wallets
from lnbits.core import services, models


def main() -> None:
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    wallet_name = os.getenv("WALLET_NAME")

    print(f"Creating user {username}")
    user = create_user_account(username, password, wallet_name)

    node_balance = asyncio.run(check_node_balance())

    print(f"Funding user with {node_balance} sats")
    fund_user_account(user, node_balance)


def create_user_account(name: str, password: str, wallet_name: str) -> None:
    account = models.Account(
        id=uuid4().hex,
        username=name
    )
    account.hash_password(password)

    return asyncio.run(services.create_user_account_no_ckeck(account, wallet_name))


async def check_node_balance() -> int:
    wallet = wallets.LndWallet()
    status = await wallet.status()
    return int(status.balance_msat / 1000)


def fund_user_account(user: models.User, sats: int) -> None:
    wallet = user.wallets[0]
    asyncio.run(services.update_wallet_balance(wallet, sats))


if __name__ == "__main__":
    main()
