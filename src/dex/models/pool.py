from typing import List
from pydantic import BaseModel

from src.database.models import PoolDao
from src.utils.address import ValidatedAddress, ValidatedAddressOrNone


class Pool(BaseModel):
    address: ValidatedAddress
    apy_1d: float | None = None
    apy_30d: float | None = None
    apy_7d: float | None = None
    collected_token0_protocol_fee: float
    collected_token1_protocol_fee: float
    deprecated: bool
    lp_account_address: ValidatedAddressOrNone = None
    lp_balance: int | None = None
    lp_fee: int | None = None
    lp_price_usd: float | None = None
    lp_total_supply: float
    lp_total_supply_usd: float | None = None
    lp_wallet_address: ValidatedAddressOrNone = None
    protocol_fee: int
    protocol_fee_address: ValidatedAddress
    ref_fee: int
    reserve0: int
    reserve1: int
    router_address: ValidatedAddress
    token0_balance: int | None = None
    token1_balance: int | None = None
    token0_address: ValidatedAddress
    token1_address: ValidatedAddress

    @staticmethod
    def from_pool_dao(pool_dao: PoolDao) -> "Pool":
        return Pool(
            address=pool_dao.address,
            apy_1d=pool_dao.apy_1d,
            apy_30d=pool_dao.apy_30d,
            apy_7d=pool_dao.apy_7d,
            collected_token0_protocol_fee=pool_dao.collected_token0_protocol_fee,  # noqa
            collected_token1_protocol_fee=pool_dao.collected_token1_protocol_fee,  # noqa
            deprecated=pool_dao.deprecated,
            lp_account_address=pool_dao.lp_account_address,
            lp_balance=pool_dao.lp_balance,
            lp_fee=pool_dao.lp_fee,
            lp_price_usd=pool_dao.lp_price_usd,
            lp_total_supply=pool_dao.lp_total_supply,
            lp_total_supply_usd=pool_dao.lp_total_supply_usd,
            lp_wallet_address=pool_dao.lp_wallet_address,
            protocol_fee=pool_dao.protocol_fee,
            protocol_fee_address=pool_dao.protocol_fee_address,
            ref_fee=pool_dao.ref_fee,
            reserve0=pool_dao.reserve0,
            reserve1=pool_dao.reserve1,
            router_address=pool_dao.router_address,
            token0_balance=pool_dao.token0_balance,
            token1_balance=pool_dao.token1_balance,
            token0_address=pool_dao.token0_address,
            token1_address=pool_dao.token1_address,
        )


class Pools(BaseModel):
    pool_list: List[Pool]


class PoolData(BaseModel):
    reserve0: int
    reserve1: int
    token0_wallet_address: ValidatedAddress
    token1_wallet_address: ValidatedAddress
    lp_fee: int
    protocol_fee: int
    ref_fee: int
    protocol_fee_address: ValidatedAddress
    collected_token0_protocol_fee: int
    collected_token1_protocol_fee: int
