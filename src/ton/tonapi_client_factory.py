from pytonapi import AsyncTonapi
from src.config import config


class TonapiClientFactory:
    tonapi_key: str = config.ton_console.api_key.get_secret_value()
    tonapi_client: AsyncTonapi = None
    max_rps: int = 1
    max_retries: int = 10

    @classmethod
    def get_tonapi_client(cls) -> AsyncTonapi:
        if cls.tonapi_client:
            return cls.tonapi_client

        cls.tonapi_client = AsyncTonapi(
            api_key=cls.tonapi_key,
            max_retries=cls.max_retries,
        )

        return cls.tonapi_client
