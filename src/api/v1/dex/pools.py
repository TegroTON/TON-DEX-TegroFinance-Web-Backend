from src.dex.http_api import (
    get_pool_for_wallet_by_assets_addresses,
    get_pools_for_wallet,
)

from typing import Annotated
from fastapi import Body

from src.database.dal import pool_dal
from src.dex.models import Pool


async def get_pools_for_wallet_endpoint(wallet_address: str):
    pools = await get_pools_for_wallet(wallet_address)

    return pools


async def get_pools_for_wallet_by_assets_addresses_endpoint(
    wallet_address: str,
    token0_contract_address: Annotated[str, Body()],
    token1_contract_address: Annotated[str, Body()],
):
    pool = await get_pool_for_wallet_by_assets_addresses(
        wallet_address,
        token0_contract_address,
        token1_contract_address,
    )

    return pool


async def get_pools_endpoint():
    pools = await pool_dal.get_pools(include_deprecated=True)

    pools_response = list(map(lambda pool: Pool.from_pool_dao(pool), pools))

    return pools_response
