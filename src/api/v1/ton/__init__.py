from fastapi import FastAPI

from .schemas import GetJettonsBalancesResponse, TokenInfoResponse
from .wallets import get_jettons_balances_endpoint
from .token import get_info_token_endpoint


def register_routes(app: FastAPI):
    app.add_api_route(
        path="/api/v1/wallet/{wallet_address}/get_balances",
        endpoint=get_jettons_balances_endpoint,
        response_model=GetJettonsBalancesResponse,
        methods=["GET"],
    )
    
    app.add_api_route(
        path="/api/v1/token/get_token_info",
        endpoint=get_info_token_endpoint,
        response_model=TokenInfoResponse,
        methods=["GET"],
    )
