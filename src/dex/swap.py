import time

from tonsdk.utils import Address

from src.config import config
from src.database.dal import account_dal, pool_dal, transaction_dal
from src.dex.models.transaction import MessageData
from src.utils.address import validate_address

from .exceptions import NotEnoughLiquidityError
from .models.swap import SwapRequest, SwapSimulateRequest, SwapSimulateResponse
from .models.transaction import TransactionData
from .ston_fi_contracts.router_factory import RouterFactory
from .utils import (
    calculate_fee_in_nanotons,
    calculate_in_amount,
    calculate_out_amount,
    calculate_price_impact,
)

PROXY_TON_ADDRESS = validate_address(config.ston_fi.proxy_ton_address)
TON_CONTRACT_ADDRESS = validate_address(config.ston_fi.ton_contract_address)


async def swap(
    swap_data: SwapRequest,
) -> TransactionData:
    router = RouterFactory.get_router()

    user_wallet_address = validate_address(swap_data.userWalletAddress)
    ask_jetton_address = validate_address(swap_data.askJettonAddress)
    offer_jetton_address = validate_address(swap_data.offerJettonAddress)
    referral_address = (
        Address(swap_data.referralAddress)
        if swap_data.referralAddress
        else None
    )

    account = await account_dal.get_account(user_wallet_address)

    valid_until = int(time.time() + 60 * 10)

    query_id = await transaction_dal.create_transaction(
        account_id=account.id,
        router_address=validate_address(router.address),
        user_wallet_address=user_wallet_address,
        offer_jetton_address=swap_data.offerJettonAddress,
        offer_amount=swap_data.offerAmount,
        ask_jetton_address=ask_jetton_address,
        min_ask_amount=swap_data.minAskAmount,
        forward_gas_amount=swap_data.forwardGasAmount,
        referral_address=swap_data.referralAddress,
        valid_until=valid_until,
    )

    fee_nanotons = await calculate_fee_in_nanotons(
        offer_amount=swap_data.offerAmount,
        offer_contract_address=swap_data.offerJettonAddress,
    )

    fee_message_data = MessageData(
        to=config.swap.ton_fee_address,
        amount=fee_nanotons,
    )

    if swap_data.offerJettonAddress == TON_CONTRACT_ADDRESS:
        swap_message_data = await router.build_swap_proxy_ton_tx_params(
            user_wallet_address=user_wallet_address,
            proxy_ton_address=PROXY_TON_ADDRESS,
            ask_jetton_contract_address=ask_jetton_address,
            offer_amount=swap_data.offerAmount,
            min_ask_amount=swap_data.minAskAmount,
            forward_gas_amount=swap_data.forwardGasAmount,
            referral_address=swap_data.referralAddress,
            query_id=query_id,
        )
    else:
        if ask_jetton_address == TON_CONTRACT_ADDRESS:
            ask_jetton_address = PROXY_TON_ADDRESS

        swap_message_data = await router.build_swap_jetton_tx_params(
            user_wallet_address=user_wallet_address,
            offer_jetton_contract_address=offer_jetton_address,
            ask_jetton_contract_address=ask_jetton_address,
            offer_amount=swap_data.offerAmount,
            min_ask_amount=swap_data.minAskAmount,
            forward_gas_amount=swap_data.forwardGasAmount,
            referral_address=referral_address,
            query_id=query_id,
        )

    return TransactionData(
        valid_until=valid_until,
        messages=[fee_message_data, swap_message_data],
    )


async def simulate_swap(
    swap_data: SwapSimulateRequest,
) -> SwapSimulateResponse:
    pool = await pool_dal.get_pool_for_assets(
        token0_address=swap_data.offer_address,
        token1_address=swap_data.ask_address,
    )
    router = RouterFactory.get_router()
    pool_data = await router.get_pool_data(Address(pool.address))

    in_reserved, out_reserved = (
        (pool_data.reserve0, pool_data.reserve1)
        if pool.token0_address == swap_data.offer_address
        else (pool_data.reserve1, pool_data.reserve0)
    )

    ask_units, protocol_fee_units, ref_fee_units = calculate_out_amount(
        has_ref=bool(swap_data.referral_address),
        amount_in=int(swap_data.units),
        reserve_in=in_reserved,
        reserve_out=out_reserved,
        lp_fee=pool_data.lp_fee,
        protocol_fee=pool_data.protocol_fee,
        ref_fee=pool_data.ref_fee,
    )

    price_impact = calculate_price_impact(
        amount=int(swap_data.units),
        reserved=in_reserved,
    )

    swap_data.slippage_tolerance /= 100

    min_ask_units = (
        int(ask_units * (1 - swap_data.slippage_tolerance))
        if ask_units > 0
        else 0
    )

    swap_rate = (
        ask_units / int(swap_data.units) if int(swap_data.units) > 0 else 0
    )

    fee_percent = (
        (protocol_fee_units + ref_fee_units) / ask_units
        if ask_units > 0
        else 0
    )

    fee_nanotons = await calculate_fee_in_nanotons(
        offer_amount=int(swap_data.units),
        offer_contract_address=swap_data.offer_address,
    )

    response = SwapSimulateResponse(
        ask_address=swap_data.ask_address,
        ask_units=ask_units,
        fee_address=swap_data.ask_address,
        fee_percent=fee_percent,
        fee_units=int(protocol_fee_units + ref_fee_units),
        min_ask_units=min_ask_units,
        offer_address=swap_data.offer_address,
        offer_units=int(swap_data.units),
        pool_address=pool.address,
        price_impact=price_impact,
        router_address=pool.router_address,
        slippage_tolerance=swap_data.slippage_tolerance,
        swap_rate=swap_rate,
        ton_fee_units=fee_nanotons,
    )

    return response


async def simulate_swap_reverse(swap_data: SwapSimulateRequest):
    pool = await pool_dal.get_pool_for_assets(
        token0_address=swap_data.offer_address,
        token1_address=swap_data.ask_address,
    )
    router = RouterFactory.get_router()
    pool_data = await router.get_pool_data(Address(pool.address))

    in_reserved, out_reserved = (
        (pool_data.reserve0, pool_data.reserve1)
        if pool.token0_address == swap_data.offer_address
        else (pool_data.reserve1, pool_data.reserve0)
    )

    if out_reserved < swap_data.units:
        raise NotEnoughLiquidityError()

    offer_units = calculate_in_amount(
        has_ref=bool(swap_data.referral_address),
        amount_out=swap_data.units,
        reserve_in=in_reserved,
        reserve_out=out_reserved,
        lp_fee=pool_data.lp_fee,
        protocol_fee=pool_data.protocol_fee,
        ref_fee=pool_data.ref_fee,
        slippage_tolerance=swap_data.slippage_tolerance,
    )

    price_impact = calculate_price_impact(
        amount=int(offer_units),
        reserved=in_reserved,
    )

    swap_data.slippage_tolerance /= 100

    min_ask_units = swap_data.units

    swap_rate = (swap_data.units / offer_units) if offer_units > 0 else 0

    protocol_fee_units = (
        min_ask_units
        * (100 + swap_data.slippage_tolerance)
        / (10_000 * pool_data.protocol_fee)
    )

    ref_fee_units = (
        (
            min_ask_units
            * (100 + swap_data.slippage_tolerance)
            / (10_000 * pool_data.ref_fee)
        )
        if swap_data.referral_address
        else 0
    )

    fee_percent = (
        (protocol_fee_units + ref_fee_units)
        / min_ask_units
        * (100 + swap_data.slippage_tolerance)
        if min_ask_units > 0
        else 0
    )

    fee_nanotons = await calculate_fee_in_nanotons(
        offer_amount=offer_units,
        offer_contract_address=swap_data.offer_address,
    )

    response = SwapSimulateResponse(
        ask_address=swap_data.ask_address,
        ask_units=min_ask_units,
        fee_address=swap_data.ask_address,
        fee_percent=fee_percent,
        fee_units=int(protocol_fee_units + ref_fee_units),
        min_ask_units=min_ask_units,
        offer_address=swap_data.offer_address,
        offer_units=offer_units,
        pool_address=pool.address,
        price_impact=price_impact,
        router_address=pool.router_address,
        slippage_tolerance=swap_data.slippage_tolerance,
        swap_rate=swap_rate,
        ton_fee_units=fee_nanotons,
    )

    return response
