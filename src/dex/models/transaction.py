from typing import List

from pydantic import BaseModel

from src.utils.address import ValidatedAddress


class MessageData(BaseModel):
    to: ValidatedAddress
    amount: int
    payload: str | None = None


class TransactionData(BaseModel):
    valid_until: int
    messages: List[MessageData]
