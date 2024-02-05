from src.dex.exceptions import NotEnoughLiquidityError
from src.dex.models import SwapRequest, SwapSimulateRequest
from src.dex.models.transaction import TransactionData
from src.dex.swap import simulate_swap, simulate_swap_reverse, swap

from .schemas import DexError


async def swap_endpoint(swap_data: SwapRequest) -> TransactionData:
    return await swap(swap_data)


async def simulate_swap_endpoint(
    request_data: SwapSimulateRequest,
):
    return await simulate_swap(request_data)


async def simulate_reverse_swap_endpoint(
    request_data: SwapSimulateRequest,
):
    try:
        return await simulate_swap_reverse(request_data)
    except NotEnoughLiquidityError as e:
        return DexError(
            type="error",
            code=e.code,
            message="Not enough liquidity",
        )
