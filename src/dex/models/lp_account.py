from pydantic import BaseModel
from tonsdk.utils import Address


class LpAccountData(BaseModel):
    token0_address: Address
    token1_address: Address
    token0_balance: int
    token1_balance: int

    class Config:
        arbitrary_types_allowed = True
