from fastapi import Depends

from src.config import config
from src.ton.wallet import get_balances, get_ton_balance

from .schemas import GetJettonsBalancesRequest, GetJettonsBalancesResponse


async def get_jettons_balances_endpoint(
    request: GetJettonsBalancesRequest = Depends(),
):
    jettons_balances = await get_balances(request.wallet_address)

    jettons_balances_data = {
        jetton_data.jetton.address.to_userfriendly(True): jetton_data.balance
        for jetton_data in jettons_balances.balances
    }

    ton_balance = await get_ton_balance(request.wallet_address)

    jettons_balances_data[config.ton.ton_contract_address] = ton_balance

    response = GetJettonsBalancesResponse(balances=jettons_balances_data)

    return response
