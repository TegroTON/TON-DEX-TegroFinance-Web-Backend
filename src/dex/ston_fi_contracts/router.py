from pytonapi import AsyncTonapi
from tonsdk.boc import Cell, begin_cell
from tonsdk.utils import Address, bytes_to_b64str

from src.ton.utils import (create_jetton_transfer_body,
                           get_jetton_wallet_address, parse_address_from_bytes)

from ..models import PoolData
from ..models.lp_account import LpAccountData
from ..models.transaction import MessageData
from . import ston_constants


class Router:
    def __init__(
        self,
        address: Address,
        tonapi_client: AsyncTonapi,
    ):
        self.address = address
        self.tonapi_client = tonapi_client

    def create_swap_body(
        self,
        user_wallet_address: str,
        min_ask_amount: int,
        ask_jetton_wallet_address: str,
        referral_address: str | None = None,
    ) -> Cell:
        cell_builder = (
            begin_cell()
            .store_uint(ston_constants.DexOpCodes.SWAP, 32)
            .store_address(Address(ask_jetton_wallet_address))
            .store_coins(min_ask_amount)
            .store_address(Address(user_wallet_address))
        )

        if referral_address:
            cell_builder.store_uint(1, 1).store_address(
                Address(referral_address)
            )
        else:
            cell_builder.store_uint(0, 1)

        cell = cell_builder.end_cell()

        return cell

    def create_provide_liquidity_body(
        self,
        router_wallet_address: str,
        min_lp_out: int,
    ) -> Cell:
        cell_builder = (
            begin_cell()
            .store_uint(ston_constants.DexOpCodes.PROVIDE_LIQUIDITY, 32)
            .store_address(Address(router_wallet_address))
            .store_coins(min_lp_out)
        )

        cell = cell_builder.end_cell()

        return cell

    def create_burn_body(
        self,
        amount: int,
        user_wallet_address: str,
        query_id: int = 0,
    ) -> Cell:
        cell_builder = (
            begin_cell()
            .store_uint(ston_constants.DexOpCodes.REQUEST_BURN, 32)
            .store_uint(query_id, 64)
            .store_coins(amount)
            .store_address(Address(user_wallet_address))
        )

        cell = cell_builder.end_cell()

        return cell

    def create_provide_liquidity_activate_body(
        self,
        token0_amount: int,
        token1_amount: int,
        min_lp_out: int,
        query_id: int = 0,
    ) -> Cell:
        cell_builder = (
            begin_cell()
            .store_uint(ston_constants.DexOpCodes.DIRECT_ADD_LIQUIDITY, 32)
            .store_uint(query_id, 64)
            .store_coins(token0_amount)
            .store_coins(token1_amount)
            .store_coins(min_lp_out)
        )

        cell = cell_builder.end_cell()

        return cell

    async def build_swap_jetton_tx_params(
        self,
        user_wallet_address: str,
        offer_jetton_contract_address: str,
        ask_jetton_contract_address: str,
        offer_amount: int,
        min_ask_amount: int,
        gas_amount: int = None,
        forward_gas_amount: int = None,
        referral_address: str = None,
        query_id: int = None,
    ) -> MessageData:
        if gas_amount is None:
            gas_amount = ston_constants.SWAP_GAS_AMOUNT
        if forward_gas_amount is None:
            forward_gas_amount = ston_constants.SWAP_FORWARD_GAS_AMOUNT
        if query_id is None:
            query_id = 0

        offer_jetton_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=offer_jetton_contract_address,
            owner_wallet_address=user_wallet_address,
        )

        ask_jetton_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=ask_jetton_contract_address,
            owner_wallet_address=self.address,
        )

        forward_payload = self.create_swap_body(
            user_wallet_address=user_wallet_address,
            min_ask_amount=min_ask_amount,
            ask_jetton_wallet_address=ask_jetton_wallet_address,
            referral_address=referral_address,
        )

        payload_cell = create_jetton_transfer_body(
            to_address=self.address,
            jetton_amount=offer_amount,
            forward_payload=forward_payload,
            forward_amount=forward_gas_amount,
            query_id=query_id,
        )

        payload_str = bytes_to_b64str(payload_cell.to_boc())

        message_data = MessageData(
            to=offer_jetton_wallet_address.to_string(True, True, True),
            payload=payload_str,
            amount=gas_amount,
        )
        return message_data

    async def build_swap_proxy_ton_tx_params(
        self,
        user_wallet_address: str,
        proxy_ton_address: str,
        ask_jetton_contract_address: str,
        offer_amount: int,
        min_ask_amount: int,
        forward_gas_amount: int = None,
        referral_address: str = None,
        query_id: int = None,
    ) -> MessageData:
        if forward_gas_amount is None:
            forward_gas_amount = ston_constants.SWAP_FORWARD_GAS_AMOUNT
        if query_id is None:
            query_id = 0

        proxy_ton_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=proxy_ton_address,
            owner_wallet_address=self.address,
        )

        ask_jetton_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=ask_jetton_contract_address,
            owner_wallet_address=self.address,
        )

        forward_payload = self.create_swap_body(
            user_wallet_address=user_wallet_address,
            min_ask_amount=min_ask_amount,
            ask_jetton_wallet_address=ask_jetton_wallet_address,
            referral_address=referral_address,
        )

        payload_cell = create_jetton_transfer_body(
            to_address=self.address,
            jetton_amount=offer_amount,
            forward_payload=forward_payload,
            forward_amount=forward_gas_amount,
            query_id=query_id,
        )

        payload_str = bytes_to_b64str(payload_cell.to_boc())

        gas_amount = forward_gas_amount + offer_amount

        message_data = MessageData(
            to=proxy_ton_wallet_address.to_string(True, True, True),
            payload=payload_str,
            amount=gas_amount,
        )

        return message_data

    async def get_pool_data(
        self,
        pool_address: Address,
    ) -> PoolData:
        response = await self.tonapi_client.blockchain.execute_get_method(
            account_id=pool_address.to_string(),
            method_name="get_pool_data",
            args=[],
        )

        reserve0 = int(response.stack[0].num, 16)
        reserve1 = int(response.stack[1].num, 16)
        token0_wallet_address = parse_address_from_bytes(
            bytes.fromhex(response.stack[2].cell)
        ).to_string(True, True, True)
        token1_wallet_address = parse_address_from_bytes(
            bytes.fromhex(response.stack[3].cell)
        ).to_string(True, True, True)
        lp_fee = int(response.stack[4].num, 16)
        protocol_fee = int(response.stack[5].num, 16)
        ref_fee = int(response.stack[6].num, 16)
        protocol_fee_address = parse_address_from_bytes(
            bytes.fromhex(response.stack[7].cell)
        ).to_string(True, True, True)
        collected_token0_protocol_fee = int(response.stack[8].num, 16)
        collected_token1_protocol_fee = int(response.stack[9].num, 16)

        pool_data = PoolData(
            reserve0=reserve0,
            reserve1=reserve1,
            token0_wallet_address=token0_wallet_address,
            token1_wallet_address=token1_wallet_address,
            lp_fee=lp_fee,
            protocol_fee=protocol_fee,
            ref_fee=ref_fee,
            protocol_fee_address=protocol_fee_address,
            collected_token0_protocol_fee=collected_token0_protocol_fee,
            collected_token1_protocol_fee=collected_token1_protocol_fee,
        )

        return pool_data

    async def get_expected_tokens(
        self,
        pool_address: str,
        token0_amount: int,
        token1_amount: int,
    ) -> int:
        response = await self.tonapi_client.blockchain.execute_get_method(
            account_id=pool_address,
            method_name="get_expected_tokens",
            args=[
                f"{token1_amount}",
                f"{token0_amount}",
            ],
        )

        return int(response.stack[0].num, 16)

    async def get_lp_account_data(
        self,
        lp_account_address: str,
    ):
        response = await self.tonapi_client.blockchain.execute_get_method(
            account_id=lp_account_address,
            method_name="get_lp_account_data",
            args=[],
        )

        token0_address = parse_address_from_bytes(
            bytes.fromhex(response.stack[0].cell)
        )
        token1_address = parse_address_from_bytes(
            bytes.fromhex(response.stack[1].cell)
        )
        token0_balance = int(response.stack[2].num, 16)
        token1_balance = int(response.stack[3].num, 16)

        return LpAccountData(
            token0_address=token0_address,
            token1_address=token1_address,
            token0_balance=token0_balance,
            token1_balance=token1_balance,
        )

    async def build_provide_liquidity_jetton_tx_params(
        self,
        user_wallet_address: str,
        send_token_address: str,
        second_token_address: str,
        send_amount: int,
        min_lp_out: int,
        gas_amount: int | None = None,
        forward_gas_amount: int | None = None,
        query_id: int | None = None,
    ) -> MessageData:
        if gas_amount is None:
            gas_amount = ston_constants.PROVIDE_LP_GAS_AMOUNT
        if forward_gas_amount is None:
            forward_gas_amount = ston_constants.PROVIDE_LP_FORWARD_GAS_AMOUNT
        if query_id is None:
            query_id = 0

        jetton_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=send_token_address,
            owner_wallet_address=user_wallet_address,
        )

        router_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=second_token_address,
            owner_wallet_address=self.address.to_string(True, True),
        )

        forward_payload = self.create_provide_liquidity_body(
            router_wallet_address=router_wallet_address,
            min_lp_out=min_lp_out,
        )

        payload_cell = create_jetton_transfer_body(
            to_address=self.address.to_string(True, True),
            jetton_amount=send_amount,
            forward_amount=forward_gas_amount,
            forward_payload=forward_payload,
            query_id=query_id,
        )

        payload_str = bytes_to_b64str(payload_cell.to_boc())

        message_data = MessageData(
            to=jetton_wallet_address.to_string(True, True, True),
            amount=gas_amount,
            payload=payload_str,
        )

        return message_data

    async def build_provide_liquidity_proxy_ton_tx_params(
        self,
        proxy_ton_address: str,
        second_token_address: str,
        send_amount: int,
        min_lp_out: int,
        forward_gas_amount: int | None = None,
        query_id: int | None = None,
    ) -> MessageData:
        gas_amount = ston_constants.PROVIDE_LP_GAS_AMOUNT
        if forward_gas_amount is None:
            forward_gas_amount = ston_constants.PROVIDE_LP_FORWARD_GAS_AMOUNT
        if query_id is None:
            query_id = 0

        proxy_ton_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=proxy_ton_address,
            owner_wallet_address=self.address,
        )

        router_wallet_address = await get_jetton_wallet_address(
            tonapi_client=self.tonapi_client,
            jetton_contract_address=second_token_address,
            owner_wallet_address=self.address,
        )

        forward_payload = self.create_provide_liquidity_body(
            router_wallet_address=router_wallet_address,
            min_lp_out=min_lp_out,
        )

        payload_cell = create_jetton_transfer_body(
            to_address=self.address,
            jetton_amount=send_amount,
            forward_amount=forward_gas_amount,
            forward_payload=forward_payload,
            query_id=query_id,
        )

        payload_str = bytes_to_b64str(payload_cell.to_boc())

        gas_amount = forward_gas_amount + send_amount

        message_data = MessageData(
            to=proxy_ton_wallet_address.to_string(True, True, True),
            amount=gas_amount,
            payload=payload_str,
        )

        return message_data

    async def build_burn_tx_params(
        self,
        amount: int,
        user_lp_wallet_address: str,
        user_wallet_address: str,
        gas_amount: int | None = None,
        query_id: int = 0,
    ) -> MessageData:
        if not gas_amount:
            gas_amount = ston_constants.BURN

        payload_cell = self.create_burn_body(
            amount=amount,
            user_wallet_address=user_wallet_address,
            query_id=query_id,
        )

        payload_str = bytes_to_b64str(payload_cell.to_boc())

        return MessageData(
            to=user_lp_wallet_address,
            amount=gas_amount,
            payload=payload_str,
        )

    async def build_provide_liquidity_activate_tx_params(
        self,
        token0_amount: int,
        token1_amount: int,
        min_lp_out: int,
        lp_account_address: str,
        gas_amount: int | None = None,
    ) -> MessageData:
        if not gas_amount:
            gas_amount = ston_constants.DIRECT_ADD_LP

        payload_cell = self.create_provide_liquidity_activate_body(
            token0_amount=token0_amount,
            token1_amount=token1_amount,
            min_lp_out=min_lp_out,
        )

        payload_str = bytes_to_b64str(payload_cell.to_boc())

        return MessageData(
            to=lp_account_address,
            amount=gas_amount,
            payload=payload_str,
        )
