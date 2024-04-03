from typing import List
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class StonFiSettings(BaseSettings):
    base_url: str
    proxy_ton_address: str
    ton_contract_address: str
    router_address: str


class Database(BaseSettings):
    dev_mode: bool

    dev_url_async: str
    dev_url_sync: str

    @property
    def url(self) -> str:
        return self.dev_url_async

    @property
    def url_sync(self) -> str:
        return self.dev_url_sync


class TonConsole(BaseSettings):
    api_key: SecretStr


class Ton(BaseSettings):
    ton_contract_address: str
    tgr_contract_address: str
    fnz_contract_address: str
    scale_contract_address: str
    host_url: str


class Swap(BaseSettings):
    fee_percent: float
    tgr_cashback_percent: float
    ton_fee_address: str


class Server(BaseSettings):
    domain: str
    cors_allow_origins: List[str]


class JWT(BaseSettings):
    cookie_secure: bool


class Config(BaseSettings):
    ton_console: TonConsole

    ton: Ton

    secret: SecretStr
    algorithm: str

    jwt: JWT

    ston_fi: StonFiSettings

    swap: Swap

    server: Server

    model_config = SettingsConfigDict(
        env_file=".env.dist",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    database: Database


config = Config()
