from src.config import config
from src.ton.schemas import TokenInfo
import httpx
import json
import logging
logger = logging.getLogger("ton-debug")

async def get_info_token(address: str) -> TokenInfo:
        """
        Get token data info.
        """
        timeout = httpx.Timeout(120)
        try:
            async with httpx.AsyncClient(timeout=timeout) as session:
                session: httpx.AsyncClient
                params = {"address":address}
                url = f"{config.ton.host_url}/api/v2/getTokenData"
                response = await session.request("GET", url=url, params= params,headers={"Content-Type":"application/json"})
                jsonStr = response.json()
                resData = json.loads(json.dumps(jsonStr))
                return TokenInfo.from_dict(resData)
        except httpx.LocalProtocolError as err:
            logger.error(err)