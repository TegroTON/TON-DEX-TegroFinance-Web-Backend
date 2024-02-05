import time
from typing import List

from tonsdk.utils import Address

from src.config import config
from src.database.dal import pool_dal
from src.dex.http_api import get_pools_for_wallet
from src.dex.models.transaction import MessageData, TransactionData
from src.dex.ston_fi_contracts.router import Router
from src.utils.address import validate_address

from .models.liquidity import SimulateProvideLiquidityResponse
from .ston_fi_contracts.router_factory import RouterFactory

PROXY_TON_ADDRESS = validate_address(config.ston_fi.proxy_ton_address)
TON_CONTRACT_ADDRESS = validate_address(config.ston_fi.ton_contract_address)


async def create_provide_liquidity_message(
    router: Router,
    user_wallet_address: str,
    send_token_address: str,
    second_token_address: str,
    send_amount: int,
    min_lp_out: int,
) -> MessageData:
    if send_token_address == TON_CONTRACT_ADDRESS:
        message_data = (
            await router.build_provide_liquidity_proxy_ton_tx_params(
                proxy_ton_address=PROXY_TON_ADDRESS,
                second_token_address=second_token_address,
                send_amount=send_amount,
                min_lp_out=min_lp_out,
            )
        )
    else:
        if second_token_address == TON_CONTRACT_ADDRESS:
            second_token_address = PROXY_TON_ADDRESS

        # print(second_token_address)

        message_data = await router.build_provide_liquidity_jetton_tx_params(
            user_wallet_address=user_wallet_address,
            send_token_address=send_token_address,
            second_token_address=second_token_address,
            send_amount=send_amount,
            min_lp_out=min_lp_out,
        )

    return message_data


async def provide_liquidity(
    user_wallet_address: str,
    token0_address: str,
    token1_address: str,
    token0_amount: int,
    token1_amount: int,
    min_lp_out: int,
) -> List[MessageData]:
    router = RouterFactory.get_router()

    token0_send_message = await create_provide_liquidity_message(
        router=router,
        user_wallet_address=user_wallet_address,
        send_token_address=token0_address,
        second_token_address=token1_address,
        send_amount=token0_amount,
        min_lp_out=min_lp_out,
    )

    token1_send_message = await create_provide_liquidity_message(
        router=router,
        user_wallet_address=user_wallet_address,
        send_token_address=token1_address,
        second_token_address=token0_address,
        send_amount=token1_amount,
        min_lp_out=min_lp_out,
    )

    valid_until = int(time.time() + 60 * 10)

    transaction_data = TransactionData(
        valid_until=valid_until,
        messages=[token0_send_message, token1_send_message],
    )

    return transaction_data


async def complete_provide_liquidity(
    user_wallet_address: str,
    send_token_address: str,
    second_token_address: str,
    send_amount: int,
    min_lp_out: int,
) -> TransactionData:
    router = RouterFactory.get_router()

    message_data = await create_provide_liquidity_message(
        router=router,
        user_wallet_address=user_wallet_address,
        send_token_address=send_token_address,
        second_token_address=second_token_address,
        send_amount=send_amount,
        min_lp_out=min_lp_out,
    )

    valid_until = int(time.time() + 60 * 10)

    transaction_data = TransactionData(
        valid_until=valid_until,
        messages=[message_data],
    )

    return transaction_data


async def complete_provide_liquidity_activate(
    token0_amount: int,
    token1_amount: int,
    min_lp_out: int,
    lp_account_address: str,
) -> TransactionData:
    router = RouterFactory.get_router()

    message_data = await router.build_provide_liquidity_activate_tx_params(
        token0_amount=token0_amount,
        token1_amount=token1_amount,
        min_lp_out=min_lp_out,
        lp_account_address=lp_account_address,
    )

    valid_until = int(time.time() + 60 * 10)

    transaction_data = TransactionData(
        valid_until=valid_until,
        messages=[message_data],
    )

    return transaction_data


async def simulate_provide_liquidity(
    token0_address: str,
    token1_address: str,
    token0_amount: int,
    token1_amount: int,
    slippage_tolerance: float,
) -> SimulateProvideLiquidityResponse:
    pool = await pool_dal.get_pool_for_assets(
        token0_address=token0_address,
        token1_address=token1_address,
    )

    router = RouterFactory.get_router()
    pool_data = await router.get_pool_data(pool_address=Address(pool.address))

    token0_reserve, token1_reserve = (
        (pool_data.reserve0, pool_data.reserve1)
        if pool.token0_address == token0_address
        else (pool_data.reserve1, pool_data.reserve0)
    )

    if token0_amount != 0:
        token1_amount = int(token0_amount * (token1_reserve / token0_reserve))
        estimated_share_of_pool = (
            round(token0_amount / (token0_reserve + token0_amount), 4) * 100
        )
    else:
        token0_amount = int(token1_amount * (token0_reserve / token1_reserve))
        estimated_share_of_pool = (
            round(token1_amount / (token1_reserve + token1_amount), 4) * 100
        )

    expected_tokens = await router.get_expected_tokens(
        pool_address=pool.address,
        token0_amount=token0_amount
        if pool.token0_address == token0_address
        else token1_amount,
        token1_amount=token1_amount
        if pool.token0_address == token0_address
        else token0_amount,
    )

    min_expected_tokens = int(expected_tokens * (1 - slippage_tolerance / 100))

    return SimulateProvideLiquidityResponse(
        token0_amount=token0_amount,
        token1_amount=token1_amount,
        min_expected_tokens=min_expected_tokens,
        expected_tokens=expected_tokens,
        estimated_share_of_pool=estimated_share_of_pool,
        action="provide",
    )


async def simulate_complete_provide_liquidity(
    token0_address: str,
    token1_address: str,
    token0_amount: int,
    token1_amount: int,
    slippage_tolerance: float,
    lp_account_address: str | None = None,
):
    if not lp_account_address:
        return await simulate_provide_liquidity(
            token0_address=token0_address,
            token1_address=token1_address,
            token0_amount=token0_amount,
            token1_amount=token1_amount,
            slippage_tolerance=slippage_tolerance,
        )

    pool = await pool_dal.get_pool_for_assets(
        token0_address=token0_address,
        token1_address=token1_address,
    )

    pool_address = Address(pool.address)

    router = RouterFactory.get_router()

    pool_data = await router.get_pool_data(pool_address=pool_address)

    token0_reserve, token1_reserve = (
        (pool_data.reserve0, pool_data.reserve1)
        if pool.token0_address == token0_address
        else (pool_data.reserve1, pool_data.reserve0)
    )

    lp_account_data = await router.get_lp_account_data(
        lp_account_address=lp_account_address
    )
    token0_balance, token1_balance = (
        (lp_account_data.token0_balance, lp_account_data.token1_balance)
        if pool.token0_address == token0_address
        else (lp_account_data.token1_balance, lp_account_data.token0_balance)
    )

    needs_completion = token0_balance > 0 or token1_balance > 0
    needs_second_token_provide = (token0_balance > 0) ^ (token1_balance > 0)
    rate_changed = (
        token0_balance > 0
        and token1_balance > 0
        and token0_reserve / token1_reserve != token0_balance / token1_balance
    )

    if not needs_completion:
        if token0_amount != 0:
            token1_amount = int(
                token0_amount * (token1_reserve / token0_reserve)
            )
        else:
            token0_amount = int(
                token1_amount * (token0_reserve / token1_reserve)
            )
        send_token_address = token0_address
        send_amount = None
        action = "provide"

    elif needs_second_token_provide:
        if token0_balance == 0:
            token0_amount = int(
                token1_amount * (token0_reserve / token1_reserve)
            )
            token1_amount = token1_balance
            send_token_address = token0_address
            send_amount = None
            action = "provide_second"
        else:
            token0_amount = token0_balance
            token1_amount = int(
                token0_amount * (token1_reserve / token0_reserve)
            )
            send_token_address = token1_address
            send_amount = None
            action = "provide_second"

    elif rate_changed:
        old_rate = token0_balance / token1_balance
        new_rate = token0_reserve / token1_reserve

        if new_rate > old_rate:
            token0_amount = int(token1_balance * new_rate)
            token1_amount = token1_balance
            send_token_address = token0_address
            send_amount = token0_amount - token0_balance
        else:
            token0_amount = token0_balance
            token1_amount = int(token0_balance / new_rate)
            send_token_address = token1_address
            send_amount = token1_amount - token1_balance
        action = "provide_additional_amount"
    else:
        token0_amount = token0_balance
        token1_amount = token1_balance
        action = "direct_add_provide"
        send_amount = None
        send_token_address = None

    expected_tokens = await router.get_expected_tokens(
        pool_address=pool.address,
        token0_amount=token0_amount
        if pool.token0_address == token0_address
        else token1_amount,
        token1_amount=token1_amount
        if pool.token0_address == token0_address
        else token0_amount,
    )

    min_expected_tokens = int(expected_tokens * (1 - slippage_tolerance / 100))

    estimated_share_of_pool = (
        round(token0_amount / (token0_reserve + token0_amount), 4) * 100
    )

    return SimulateProvideLiquidityResponse(
        token0_amount=token0_amount,
        token1_amount=token1_amount,
        min_expected_tokens=min_expected_tokens,
        expected_tokens=expected_tokens,
        estimated_share_of_pool=estimated_share_of_pool,
        action=action,
        send_token_address=send_token_address,
        send_amount=send_amount,
    )


async def remove_liquidity(
    user_wallet_address: str,
    token0_address: str,
    token1_address: str,
    lp_amount: int,
) -> TransactionData:
    router = RouterFactory.get_router()

    pools = await get_pools_for_wallet(user_wallet_address)

    pool = None
    for pool_data in pools:
        if (
            pool_data.token0_address == token0_address
            and pool_data.token1_address == token1_address
            or pool_data.token0_address == token1_address
            and pool_data.token1_address == token0_address
        ):
            pool = pool_data
            break

    if not pool:
        # TODO: return error
        return None

    message_data = await router.build_burn_tx_params(
        user_wallet_address=user_wallet_address,
        amount=lp_amount,
        user_lp_wallet_address=pool.lp_wallet_address,
    )

    valid_until = int(time.time() + 60 * 10)

    return TransactionData(
        valid_until=valid_until,
        messages=[message_data],
    )
