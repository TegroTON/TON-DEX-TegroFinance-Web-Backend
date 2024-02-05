from typing import List
from urllib.parse import urlencode

import httpx

from src.config import config
from src.database.models import TransactionDao
from src.database.dal import transaction_dal
from src.dex.utils import calculate_fee_in_nanotons

from .models import (
    Asset,
    Assets,
    CheckTransactionRequest,
    CheckTransactionResponse,
    CheckTransactionResponseType,
    Pool,
    Pools,
    SwapSimulateRequest,
    SwapSimulateResponse,
)


async def get_wallet_assets(wallet_address: str) -> List[Asset]:
    url = f"{config.ston_fi.base_url}/v1/wallets/{wallet_address}/assets"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        response.raise_for_status()

        data_dict = response.json()

    validated_assets = Assets.model_validate(data_dict)

    return validated_assets.asset_list


async def get_assets() -> Assets:
    url = f"{config.ston_fi.base_url}/v1/assets"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        response.raise_for_status()

        data_dict = response.json()

        return Assets.model_validate(data_dict)


async def get_pools() -> Pools:
    url = f"{config.ston_fi.base_url}/v1/pools"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        response.raise_for_status()

        data_dict = response.json()

        return Pools.model_validate(data_dict)


async def simulate_swap(
    swap_data: SwapSimulateRequest,
    reverse: bool = False,
) -> SwapSimulateResponse:
    url = f"{config.ston_fi.base_url}/v1/{'reverse_' if reverse else ''}swap/simulate"  # noqa

    if int(swap_data.units) > 0:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                params=swap_data.model_dump(exclude_none=True),
            )
            response.raise_for_status()

            data_dict = response.json()
            data_dict["ton_fee_units"] = await calculate_fee_in_nanotons(
                offer_amount=int(swap_data.units),
                offer_contract_address=swap_data.offer_address,
            )
            response = SwapSimulateResponse.model_validate(data_dict)
    else:
        return None

    response.offer_units = int(
        response.offer_units * (1.01 + response.slippage_tolerance / 100)
    )
    response.min_ask_units = response.ask_units

    return response


async def get_pools_for_wallet(wallet_address: str) -> List[Pool]:
    url = f"{config.ston_fi.base_url}/v1/wallets/{wallet_address}/pools"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        response.raise_for_status()

        data_dict = response.json()

    pools = list(
        filter(
            lambda pool: pool.token0_balance is not None
            or pool.token1_balance is not None
            or pool.lp_balance is not None,
            Pools.model_validate(data_dict).pool_list,
        )
    )

    return pools


async def get_pool_for_wallet_by_assets_addresses(
    wallet_address: str,
    token0_address: str,
    token1_address: str,
) -> Pool | None:
    url = f"{config.ston_fi.base_url}/v1/wallets/{wallet_address}/pools"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        response.raise_for_status()

        data_dict = response.json()

    pools = Pools.model_validate(data_dict).pool_list

    for pool in pools:
        if {
            token0_address,
            token1_address,
        } == {
            pool.token0_address,
            pool.token1_address,
        }:
            return pool

    return None


async def update_swap_transaction(transaction: TransactionDao):
    url = f"{config.ston_fi.base_url}/v1/swap/status"

    request_data = CheckTransactionRequest(
        query_id=transaction.query_id,
        router_address=transaction.router_address,
        owner_address=transaction.user_wallet_address,
    )

    params = urlencode(request_data.model_dump(exclude_none=True))

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=url,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        data_dict = response.json()

    if data_dict["@type"] == CheckTransactionResponseType.NOT_FOUND.value:
        return

    response = CheckTransactionResponse.model_validate(data_dict)

    if response.exit_code == "swap_ok":
        await transaction_dal.set_transaction_confirmed(transaction.id)
