from typing import Tuple

from src.config import config
from src.database.dal import pool_dal

FEE_DIVIDER = 10000


def calculate_out_amount(
    has_ref: int,
    amount_in: int,
    reserve_in: int,
    reserve_out: int,
    lp_fee: int,
    protocol_fee: int,
    ref_fee: int,
) -> Tuple[int, int, int]:
    if amount_in <= 0:
        return (0, 0, 0)

    amount_in_with_fee = amount_in / 1_000_000_000 * (FEE_DIVIDER - lp_fee)
    base_out = (amount_in_with_fee * reserve_out / 1_000_000_000) / (
        reserve_in / 1_000_000_000 * FEE_DIVIDER + amount_in_with_fee
    )

    protocol_fee_out = 0
    ref_fee_out = 0

    if protocol_fee > 0:
        protocol_fee_out = base_out * protocol_fee / FEE_DIVIDER

    if has_ref and (ref_fee > 0):
        ref_fee_out = base_out * ref_fee / FEE_DIVIDER

    base_out -= protocol_fee_out + ref_fee_out

    return (
        int(base_out * 1_000_000_000),
        int(protocol_fee_out * 1_000_000_000),
        int(ref_fee_out * 1_000_000_000),
    )


def calculate_in_amount(
    has_ref: int,
    amount_out: int,
    reserve_in: int,
    reserve_out: int,
    lp_fee: int,
    protocol_fee: int,
    ref_fee: int,
    slippage_tolerance: float,
) -> int:
    if amount_out <= 0:
        return 0

    numerator = (
        ((reserve_in / 1_000_000_000) * (amount_out / 1_000_000_000))
        * 10_000
        * 1_000_000_000
    )
    denominator = (
        (reserve_out - amount_out) / 1_000_000_000 * (10_000 - lp_fee)
    )

    amount_in = numerator / denominator + 1

    amount_in = int(
        (amount_in * (10_020 + (slippage_tolerance * 100))) // 10_000
    )

    return amount_in


def calculate_price_impact(
    amount: int,
    reserved: int,
):
    price_impact = amount / (reserved + amount) * 100

    return price_impact


async def calculate_fee_in_nanotons(
    offer_amount: int,
    offer_contract_address: str,
) -> int:
    if offer_contract_address in {
        config.ton.ton_contract_address,
        config.ston_fi.proxy_ton_address,
    }:
        return int((config.swap.fee_percent / 100) * offer_amount)

    rate = await calculate_asset_ton_rate(offer_contract_address)

    return int((rate * config.swap.fee_percent / 100) * offer_amount)


async def calculate_asset_ton_rate(offer_contract_address: str) -> float:
    pool = await pool_dal.get_pool_for_assets(
        offer_contract_address, config.ton.ton_contract_address
    )

    offer_asset_reserve, ton_reserve = (
        [pool.reserve0, pool.reserve1]
        if offer_contract_address == pool.token0_address
        else [pool.reserve1, pool.reserve0]
    )

    return ton_reserve / offer_asset_reserve
