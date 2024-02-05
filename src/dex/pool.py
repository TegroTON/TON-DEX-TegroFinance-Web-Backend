from tonsdk.utils import Address

from src.database.dal import pool_dal
from src.dex.ston_fi_contracts.router_factory import RouterFactory


async def get_pool_for_tokens(token_0_address: str, token_1_address: str):
    pool = await pool_dal.get_pool_for_assets(
        token0_address=token_0_address,
        token1_address=token_1_address,
    )

    if not pool:
        return None

    router = RouterFactory.get_router()
    pool_data = await router.get_pool_data(Address(pool.address))

    if not pool_data:
        return None

    return pool_data
