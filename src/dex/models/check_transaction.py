from typing import Dict
from pydantic import BaseModel, root_validator
from enum import Enum as StrEnum
from src.utils.address import ValidatedAddress


class CheckTransactionResponseType(StrEnum):
    FOUND = "Found"
    NOT_FOUND = "NotFound"


class CheckTransactionRequest(BaseModel):
    query_id: int
    router_address: ValidatedAddress
    owner_address: ValidatedAddress


class CheckTransactionErrorResponse(BaseModel):
    type: CheckTransactionResponseType

    @root_validator(pre=True)
    def rename_type(cls, values):
        values["type"] = values["@type"]
        return values


class CheckTransactionResponse(CheckTransactionErrorResponse):
    address: ValidatedAddress
    balance_deltas: Dict[str, int]
    coins: str
    exit_code: str
    logical_time: str
    query_id: int
    tx_hash: str
