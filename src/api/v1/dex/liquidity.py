from src.dex.liquidity import (
    complete_provide_liquidity,
    complete_provide_liquidity_activate,
    provide_liquidity,
    remove_liquidity,
    simulate_complete_provide_liquidity,
)
from src.dex.models.liquidity import (
    CompleteProvideLiquidityActivateRequest,
    CompleteProvideLiquidityRequest,
    ProvideLiquidityRequest,
    RemoveLiquidityRequest,
    SimulateProvideLiquidityRequest,
)
from src.dex.models.transaction import TransactionData


async def simulate_provide_liquidity_endpoint(
    request_data: SimulateProvideLiquidityRequest,
):
    # return await simulate_provide_liquidity(
    return await simulate_complete_provide_liquidity(
        token0_address=request_data.token0_address,
        token1_address=request_data.token1_address,
        token0_amount=request_data.token0_amount,
        token1_amount=request_data.token1_amount,
        slippage_tolerance=request_data.slippage_tolerance,
        lp_account_address=request_data.lp_account_address,
    )


async def provide_liquidity_endpoint(
    request_data: ProvideLiquidityRequest,
) -> TransactionData:
    transaction_data = await provide_liquidity(
        user_wallet_address=request_data.user_wallet_address,
        token0_address=request_data.token0_address,
        token1_address=request_data.token1_address,
        token0_amount=request_data.token0_amount,
        token1_amount=request_data.token1_amount,
        min_lp_out=request_data.min_lp_out,
    )

    return transaction_data


async def complete_provide_liquidity_endpoint(
    request_data: CompleteProvideLiquidityRequest,
) -> TransactionData:
    transaction_data = await complete_provide_liquidity(
        user_wallet_address=request_data.user_wallet_address,
        send_token_address=request_data.token_address,
        second_token_address=request_data.second_token_address,
        send_amount=request_data.token_amount,
        min_lp_out=request_data.min_lp_out,
    )

    return transaction_data


async def complete_provide_liquidity_activate_endpoint(
    request_data: CompleteProvideLiquidityActivateRequest,
) -> TransactionData:
    transaction_data = await complete_provide_liquidity_activate(
        token0_amount=request_data.token0_amount,
        token1_amount=request_data.token1_amount,
        min_lp_out=request_data.min_lp_out,
        lp_account_address=request_data.lp_account_address,
    )

    return transaction_data


async def remove_liquidity_endpoint(
    request_data: RemoveLiquidityRequest,
) -> TransactionData:
    transaction_data = await remove_liquidity(
        user_wallet_address=request_data.user_wallet_address,
        token0_address=request_data.token0_address,
        token1_address=request_data.token1_address,
        lp_amount=request_data.lp_tokens_amount,
    )

    return transaction_data
