from .tonapi_client_factory import TonapiClientFactory
from pytonapi.schema.jettons import JettonsBalances


async def get_balances(owner_address: str) -> JettonsBalances:
    client = TonapiClientFactory.get_tonapi_client()

    result = await client.accounts.get_jettons_balances(
        account_id=owner_address
    )

    return result


async def get_ton_balance(owner_address: str) -> int:
    client = TonapiClientFactory.get_tonapi_client()

    result = await client.accounts.get_info(account_id=owner_address)

    return result.balance.to_nano()


async def get_wallet_public_key(wallet_address: str) -> str:
    client = TonapiClientFactory.get_tonapi_client()

    result = await client.accounts.get_public_key(account_id=wallet_address)
    public_key = result.public_key

    return public_key
