from fastapi import FastAPI

from .schemas import GetJettonsBalancesResponse
from .wallets import get_jettons_balances_endpoint


def register_routes(app: FastAPI):
    app.add_api_route(
        path="/api/v1/wallet/{wallet_address}/get_balances",
        endpoint=get_jettons_balances_endpoint,
        response_model=GetJettonsBalancesResponse,
        methods=["GET"],
    )
