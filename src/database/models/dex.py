from enum import Enum as StrEnum
from typing import Any, Dict

from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AssetKind(StrEnum):
    JETTON = "Jetton"
    WTON = "Wton"
    TON = "Ton"


class AssetDao(Base):
    blacklisted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    community: Mapped[bool] = mapped_column(Boolean, nullable=False)
    contract_address: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    decimals: Mapped[int] = mapped_column(Integer, nullable=False)
    default_symbol: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    dex_price_usd: Mapped[float] = mapped_column(Float, nullable=True)
    dex_usd_price: Mapped[float] = mapped_column(Float, nullable=True)
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    kind: Mapped[AssetKind] = mapped_column(Enum(AssetKind), nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    third_party_price_usd: Mapped[float] = mapped_column(Float, nullable=True)
    third_party_usd_price: Mapped[float] = mapped_column(Float, nullable=True)

    def update(self, **kwargs):
        update_keys = {
            "symbol",
            "default_symbol",
            "blacklisted",
            "community",
            "deprecated",
            "dex_price_usd",
            "dex_usd_price",
            "display_name",
            "image_url",
            "third_party_price_usd",
            "third_party_usd_price",
        }

        for key, value in kwargs.items():
            if key in update_keys:
                setattr(self, key, value)

    @staticmethod
    def from_dict(asset_data: Dict[str, Any]) -> "AssetDao":
        return AssetDao(**asset_data)


class PoolDao(Base):
    address: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    apy_1d: Mapped[float] = mapped_column(Float, nullable=True)
    apy_30d: Mapped[float] = mapped_column(Float, nullable=True)
    apy_7d: Mapped[float] = mapped_column(Float, nullable=True)
    collected_token0_protocol_fee: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    collected_token1_protocol_fee: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    lp_account_address: Mapped[str] = mapped_column(String, nullable=True)
    lp_balance: Mapped[float] = mapped_column(Float, nullable=True)
    lp_fee: Mapped[int] = mapped_column(BigInteger, nullable=False)
    lp_price_usd: Mapped[float] = mapped_column(Float, nullable=True)
    lp_total_supply: Mapped[int] = mapped_column(BigInteger, nullable=False)
    lp_total_supply_usd: Mapped[float] = mapped_column(Float, nullable=True)
    lp_wallet_address: Mapped[str] = mapped_column(String, nullable=True)
    protocol_fee: Mapped[int] = mapped_column(BigInteger, nullable=True)
    protocol_fee_address: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    ref_fee: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reserve0: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reserve1: Mapped[int] = mapped_column(BigInteger, nullable=False)
    router_address: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    token0_address: Mapped[str] = mapped_column(
        String,
        ForeignKey(AssetDao.contract_address),
        nullable=False,
    )
    token0_balance: Mapped[float] = mapped_column(Float, nullable=True)
    token1_address: Mapped[str] = mapped_column(
        String,
        ForeignKey(AssetDao.contract_address),
        nullable=False,
    )
    token1_balance: Mapped[float] = mapped_column(Float, nullable=True)

    token0: Mapped[AssetDao] = relationship(
        "AssetDao",
        foreign_keys=[token0_address],
    )
    token1: Mapped[AssetDao] = relationship(
        "AssetDao",
        foreign_keys=[token1_address],
    )

    @staticmethod
    def from_dict(pool_data: Dict[str, Any]) -> "PoolDao":
        return PoolDao(**pool_data)

    def update(self, **kwargs) -> None:
        update_keys = {
            "apy_1d",
            "apy_30d",
            "apy_7d",
            "collected_token0_protocol_fee",
            "collected_token1_protocol_fee",
            "deprecated",
            "lp_account_address",
            "lp_balance",
            "lp_fee",
            "lp_price_usd",
            "lp_total_supply",
            "lp_total_supply_usd",
            "lp_wallet_address",
            "protocol_fee",
            "protocol_fee_address",
            "ref_fee",
            "reserve0",
            "reserve1",
            "router_address",
            "token0_balance",
            "token1_balance",
        }

        for key, value in kwargs.items():
            if key in update_keys:
                setattr(self, key, value)
