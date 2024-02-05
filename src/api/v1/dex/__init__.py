from typing import List

from fastapi import FastAPI

from src.dex.models import Pool, SwapSimulateResponse, WalletAssetExport
from src.dex.models.liquidity import SimulateProvideLiquidityResponse
from src.dex.models.transaction import TransactionData

from .assets import get_assets_endpoint
from .liquidity import (
    complete_provide_liquidity_activate_endpoint,
    complete_provide_liquidity_endpoint,
    provide_liquidity_endpoint,
    remove_liquidity_endpoint,
    simulate_provide_liquidity_endpoint,
)
from .pools import get_pools_endpoint, get_pools_for_wallet_endpoint
from .schemas import DexError
from .swap import (
    simulate_reverse_swap_endpoint,
    simulate_swap_endpoint,
    swap_endpoint,
)


def register_routes(app: FastAPI):
    app.add_api_route(
        path="/api/v1/wallet/{wallet_address}/get_pools",
        endpoint=get_pools_for_wallet_endpoint,
        response_model=List[Pool],
        methods=["GET"],
    )

    app.add_api_route(
        path="/api/v1/swap",
        endpoint=swap_endpoint,
        methods=["POST"],
        response_model=TransactionData,
    )

    app.add_api_route(
        path="/api/v1/swap/simulate",
        endpoint=simulate_swap_endpoint,
        methods=["POST"],
        response_model=SwapSimulateResponse,
    )

    app.add_api_route(
        path="/api/v1/reverse_swap/simulate",
        endpoint=simulate_reverse_swap_endpoint,
        methods=["POST"],
        response_model=SwapSimulateResponse | DexError,
    )

    app.add_api_route(
        path="/api/v1/pools",
        endpoint=get_pools_endpoint,
        methods=["GET"],
        response_model=List[Pool],
    )

    app.add_api_route(
        path="/api/v1/assets",
        endpoint=get_assets_endpoint,
        methods=["GET"],
        response_model=List[WalletAssetExport],
    )

    app.add_api_route(
        path="/api/v1/dex/liquidity/provide/simulate",
        endpoint=simulate_provide_liquidity_endpoint,
        methods=["POST"],
        response_model=SimulateProvideLiquidityResponse,
    )

    app.add_api_route(
        path="/api/v1/dex/liquidity/provide",
        endpoint=provide_liquidity_endpoint,
        methods=["POST"],
        response_model=TransactionData,
    )

    app.add_api_route(
        path="/api/v1/dex/liquidity/provide_complete",
        endpoint=complete_provide_liquidity_endpoint,
        methods=["POST"],
        response_model=TransactionData,
    )

    app.add_api_route(
        path="/api/v1/dex/liquidity/provide_complete_activate",
        endpoint=complete_provide_liquidity_activate_endpoint,
        methods=["POST"],
        response_model=TransactionData,
    )

    app.add_api_route(
        path="/api/v1/dex/liquidity/remove",
        endpoint=remove_liquidity_endpoint,
        methods=["POST"],
        response_model=TransactionData,
    )
