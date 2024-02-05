from pydantic import AfterValidator
from tonsdk.utils import Address
from typing_extensions import Annotated


class TonAddress:
    address: str

    def __init__(self, address: str | Address):
        self.address = Address(address).to_string(True, True, True, False)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.address == Address(__value).address

        if isinstance(__value, TonAddress):
            return self.address == __value.address


def validate_address(address: str | Address) -> str:
    if isinstance(address, str):
        try:
            address = Address(address)
        except Exception:
            raise ValueError(f"Invalid address: {address}")

    address_string = address.to_string(True, True, True)

    return address_string


def validate_address_or_none(address: str | Address | None) -> str | None:
    if address is None:
        return None
    return validate_address(address)


ValidatedAddress = Annotated[str, AfterValidator(validate_address)]

ValidatedAddressOrNone = Annotated[
    str | None, AfterValidator(validate_address_or_none)
]


def compare_addresses(
    address0: str | Address,
    address1: str | Address,
) -> bool:
    if isinstance(address0, str):
        address0 = Address(address0)
    if isinstance(address1, str):
        address1 = Address(address1)

    return Address(address0) == Address(address1)
