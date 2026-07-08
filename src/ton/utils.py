from pytonapi import AsyncTonapi
from tonsdk.boc import Cell, Slice, begin_cell
from tonsdk.utils import Address, b64str_to_bytes, bytes_to_b64str
from src.ton.tonapi_client_factory import TonapiClientFactory

import logging
logger = logging.getLogger("ton-debug")

def get_address_cell(address: Address | str) -> Cell:
    if isinstance(address, str):
        address = Address(address)
    return begin_cell().store_address(address).end_cell()


def get_address_slice(address: Address | str) -> str:
    address_cell = get_address_cell(address)
    address_slice = bytes_to_b64str((address_cell).to_boc(False))

    return address_slice


def parse_address_from_cell(cell: Cell) -> Address | None:
    slice = Slice(cell)

    address = slice.read_msg_addr()

    return address


def parse_address_from_boc(boc: str) -> Address | None:
    cell = Cell.one_from_boc(b64str_to_bytes(boc))
    return parse_address_from_cell(cell)


def parse_address_from_bytes(address_bytes: bytes) -> Address | None:
    cell = Cell.one_from_boc(address_bytes)
    return parse_address_from_cell(cell)


def parse_address_from_cell_str(cell_str: str) -> Address | None:
    cell = Cell.one_from_boc(cell_str)
    return parse_address_from_cell(cell)


async def get_jetton_wallet_address(
    jetton_contract_address: str,
    owner_wallet_address: str,
    tonapi_client: AsyncTonapi | None = None,
) -> Address:
    if not tonapi_client:
        tonapi_client = TonapiClientFactory.get_tonapi_client()

    owner_wallet_address_hex = get_address_cell(owner_wallet_address)
    
    owner_wallet_address_hex_value = owner_wallet_address_hex.to_boc(False).hex()
    logger.info("wallet address: " + owner_wallet_address_hex_value)
    
    response = await tonapi_client.blockchain.execute_get_wallets_method(
        account_id=jetton_contract_address,
        method_name="get_wallet_address",
        arggs=[owner_wallet_address_hex_value],
    )

    wallet_address = parse_address_from_bytes(
        bytes.fromhex(response.stack[0].cell)
    )

    return wallet_address


def create_jetton_transfer_body(
    to_address: str,
    jetton_amount: int,
    forward_amount: int = 0,
    custom_payload: Cell = None,
    forward_payload: Cell = None,
    response_address: str = None,
    query_id: int = 0,
) -> Cell:
    response_address = Address(response_address) if response_address else None

    cell_builder = (
        begin_cell()
        .store_uint(0xF8A7EA5, 32)
        .store_uint(query_id, 64)
        .store_coins(jetton_amount)
        .store_address(Address(to_address))
        .store_address(response_address)
        .store_maybe_ref(custom_payload)
        .store_coins(forward_amount)
        .store_maybe_ref(forward_payload)
    )

    cell = cell_builder.end_cell()

    return cell


def get_address_friendly_form(address: str) -> str:
    return Address(address).to_string(True)
