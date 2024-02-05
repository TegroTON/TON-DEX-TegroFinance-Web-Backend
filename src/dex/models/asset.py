from typing import List

from pydantic import BaseModel

from src.database.models import AssetDao
from src.database.models.dex import AssetKind
from src.utils.address import ValidatedAddress, ValidatedAddressOrNone


class Asset(BaseModel):
    balance: int = 0
    blacklisted: bool
    community: bool
    contract_address: ValidatedAddress
    decimals: int
    default_symbol: bool
    deprecated: bool
    dex_price_usd: float | None = None
    dex_usd_price: float | None = None
    display_name: str | None = None
    image_url: str | None = None
    kind: AssetKind
    symbol: str
    third_party_price_usd: float | None = None
    third_party_usd_price: float | None = None
    wallet_address: ValidatedAddressOrNone = None


class Assets(BaseModel):
    asset_list: List[Asset]


class WalletAssetExport(BaseModel):
    balance: int = 0
    image_url: str | None = None
    kind: str
    wallet_address: ValidatedAddressOrNone = None
    symbol: str
    decimals: int
    contract_address: ValidatedAddress
    display_name: str | None = None

    @staticmethod
    def from_walletAsset(walletAsset: Asset) -> "WalletAssetExport":
        return WalletAssetExport(
            balance=walletAsset.balance,
            image_url=walletAsset.image_url,
            kind=walletAsset.kind,
            wallet_address=walletAsset.wallet_address,
            symbol=walletAsset.symbol,
            decimals=walletAsset.decimals,
            contract_address=walletAsset.contract_address,
            display_name=walletAsset.display_name,
        )

    @staticmethod
    def from_asset_dao(asset_dao: AssetDao) -> "WalletAssetExport":
        return WalletAssetExport(
            image_url=asset_dao.image_url,
            kind=asset_dao.kind,
            symbol=asset_dao.symbol,
            decimals=asset_dao.decimals,
            contract_address=asset_dao.contract_address,
            display_name=asset_dao.display_name,
        )


class WalletAssetsExport(BaseModel):
    asset_list: List[WalletAssetExport]
