from typing import Literal
from pydantic import BaseModel
from src.utils.address import ValidatedAddress


class SimulateProvideLiquidityRequest(BaseModel):
    token0_address: ValidatedAddress
    token1_address: ValidatedAddress
    token0_amount: int
    token1_amount: int
    slippage_tolerance: float
    user_wallet_address: ValidatedAddress | None = None
    lp_account_address: ValidatedAddress | None = None


class SimulateProvideLiquidityResponse(BaseModel):
    token0_amount: int
    token1_amount: int
    min_expected_tokens: int
    expected_tokens: int
    estimated_share_of_pool: float
    action: Literal[
        "provide",
        "provide_second",
        "provide_additional_amount",
        "direct_add_provide",
    ]
    send_token_address: ValidatedAddress | None = None
    send_amount: int | None = None


class ProvideLiquidityRequest(BaseModel):
    user_wallet_address: ValidatedAddress
    token0_address: ValidatedAddress
    token1_address: ValidatedAddress
    token0_amount: int
    token1_amount: int
    min_lp_out: int


class CompleteProvideLiquidityRequest(BaseModel):
    user_wallet_address: ValidatedAddress
    token_address: ValidatedAddress
    second_token_address: ValidatedAddress
    token_amount: int
    min_lp_out: int


class CompleteProvideLiquidityActivateRequest(BaseModel):
    token0_amount: int
    token1_amount: int
    min_lp_out: int
    lp_account_address: ValidatedAddress


class RemoveLiquidityRequest(BaseModel):
    user_wallet_address: ValidatedAddress
    token0_address: ValidatedAddress
    token1_address: ValidatedAddress
    lp_tokens_amount: int


class LpAccountData(BaseModel):
    user_address: ValidatedAddress
    pool_address: ValidatedAddress
    amount0: int
    amount1: int
