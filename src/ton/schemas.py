from typing import Any
from dataclasses import dataclass
import json
@dataclass
class Data:
    image: str
    name: str
    symbol: str
    description: str
    decimals: str

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        _image = str(obj.get("image"))
        _name = str(obj.get("name"))
        _symbol = str(obj.get("symbol"))
        _description = str(obj.get("description"))
        _decimals = str(obj.get("decimals"))
        return Data(_image, _name, _symbol, _description, _decimals)

@dataclass
class JettonContent:
    type: str
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> 'JettonContent':
        _type = str(obj.get("type"))
        _data = Data.from_dict(obj.get("data"))
        return JettonContent(_type, _data)

@dataclass
class Result:
    total_supply: float
    mintable: bool
    admin_address: str
    jetton_content: JettonContent
    jetton_wallet_code: str
    contract_type: str

    @staticmethod
    def from_dict(obj: Any) -> 'Result':
        _total_supply = float(obj.get("total_supply"))
        _mintable = True
        _admin_address = str(obj.get("admin_address"))
        _jetton_content = JettonContent.from_dict(obj.get("jetton_content"))
        _jetton_wallet_code = str(obj.get("jetton_wallet_code"))
        _contract_type = str(obj.get("contract_type"))
        return Result(_total_supply, _mintable, _admin_address, _jetton_content, _jetton_wallet_code, _contract_type)

@dataclass
class TokenInfo:
    ok: bool
    result: Result

    @staticmethod
    def from_dict(obj: Any) -> 'TokenInfo':
        _ok = obj.get("ok")
        _result = Result.from_dict(obj.get("result"))
        return TokenInfo(_ok, _result)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# token = TokenInfo.from_dict(jsonstring)
