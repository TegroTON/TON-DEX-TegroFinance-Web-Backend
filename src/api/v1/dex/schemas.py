from pydantic import BaseModel
from enum import Enum


class ResponseType(str, Enum):
    success = "success"
    error = "error"


class DexError(BaseModel):
    type: ResponseType = ResponseType.error
    code: str
    message: str
