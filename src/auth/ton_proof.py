import hashlib
from datetime import datetime

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from nacl.utils import random
from tonsdk.boc import Cell, Slice
from tonsdk.contract.wallet import WalletVersionEnum
from tonsdk.utils import Address, b64str_to_bytes, bytes_to_b64str

from src.ton.wallet import get_wallet_public_key

from .models import AuthWithTonProofRequest
from src.ton.wallets_codes import get_wallet_version


def generate_payload(ttl: int) -> str:
    payload = bytearray(random(8))

    ts = int(datetime.now().timestamp() + ttl)
    payload.extend(ts.to_bytes(8, byteorder="big"))

    return payload.hex()


async def check_ton_proof(
    payload: str,
    user_address: str,
    request: AuthWithTonProofRequest,
) -> bool:
    address = Address(user_address)
    wc = address.wc
    whash = address.hash_part

    message = bytearray()
    message.extend("ton-proof-item-v2/".encode())
    message.extend(wc.to_bytes(4, "little"))
    message.extend(whash)
    message.extend(request.proof.domain.length_bytes.to_bytes(4, "little"))
    message.extend(request.proof.domain.value.encode())
    message.extend(request.proof.timestamp.to_bytes(8, "little"))
    if payload is not None:
        message.extend(payload.encode())
    else:
        message.extend(request.proof.payload.encode())

    signature_message = bytearray()
    signature_message.extend(bytes.fromhex("ffff"))
    signature_message.extend("ton-connect".encode())
    signature_message.extend(hashlib.sha256(message).digest())

    public_key = None
    try:
        public_key = await get_wallet_public_key(
            wallet_address=address.to_string()
        )
    except Exception:
        public_key = None

    if public_key is None:
        public_key = get_public_key_from_state_init(request.proof.state_init)

    if request.proof.public_key and public_key != request.proof.public_key:
        return False

    try:
        verify_key = VerifyKey(public_key, HexEncoder)
        verify_key.verify(
            hashlib.sha256(signature_message).digest(),
            b64str_to_bytes(request.proof.signature),
        )
        return True
    except Exception:
        # print(e.with_traceback(e.__traceback__))
        pass

    return False


# const stateInit = beginCell().
#     storeBit(0). // No split_depth
#     storeBit(0). // No special
#     storeBit(1). // We have code
#     storeRef(codeCell).
#     storeBit(1). // We have data
#     storeRef(dataCell).
#     storeBit(0). // No library
#     endCell();


# const dataCell = beginCell().
#     storeUint(0, 32). // Seqno
#     storeUint(3, 32). // Subwallet ID
#     storeBuffer(keyPair.publicKey). // Public Key
#     endCell();


def get_public_key_from_state_init(state_init: str) -> str | None:
    state_init_cell: Cell = Cell.one_from_boc(b64str_to_bytes(state_init))
    state_init_slice = Slice(state_init_cell)

    _ = state_init_slice.read_bit()  # split_depth
    _ = state_init_slice.read_bit()  # special
    have_code = state_init_slice.read_bit()
    code_cell = state_init_slice.read_ref() if have_code else None  # code_cell
    if not code_cell:
        return None
    have_data = state_init_slice.read_bit()
    data_cell = state_init_slice.read_ref() if have_data else None
    _ = state_init_slice.read_bit()  # library

    if not data_cell:
        return None

    code_cell_hash = bytes_to_b64str(code_cell.bytes_hash())

    wallet_version = get_wallet_version(wallet_code_cell_hash=code_cell_hash)

    if not wallet_version:
        return None

    public_key = _get_public_key_from_data(
        data_cell=data_cell, wallet_version=wallet_version
    )

    return public_key


def _get_public_key_from_data(
    data_cell: Cell,
    wallet_version: WalletVersionEnum,
) -> str:
    data_slice = Slice(data_cell)

    if wallet_version in {
        WalletVersionEnum.v2r1,
        WalletVersionEnum.v2r2,
    }:
        _ = data_slice.read_uint(32)  # seqno
        public_key_bytes = data_slice.read_bytes(len(data_slice))[:32]
    elif wallet_version in {
        WalletVersionEnum.v3r1,
        WalletVersionEnum.v3r2,
        WalletVersionEnum.v4r1,
        WalletVersionEnum.v4r2,
    }:
        _ = data_slice.read_uint(32)  # seqno
        _ = data_slice.read_uint(32)  # subwallet_id
        public_key_bytes = data_slice.read_bytes(len(data_slice))[:32]
    elif wallet_version == WalletVersionEnum.hv2:
        _ = data_slice.read_uint(32)  # subwallet_id
        public_key_bytes = data_slice.read_bytes(len(data_slice))[:32]
    else:
        return None

    public_key = public_key_bytes.hex()

    return public_key
