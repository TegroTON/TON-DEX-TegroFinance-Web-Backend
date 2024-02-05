from src.config import config
from src.database.dal import asset_dal
from src.dex.http_api import get_wallet_assets
from src.dex.models import WalletAssetExport


async def get_balances_endpoint(wallet_address: str):
    assets = await get_wallet_assets(wallet_address)
    assets.sort(key=lambda asset: asset.balance, reverse=True)
    return [
        WalletAssetExport.from_walletAsset(asset)
        for asset in assets
        if not asset.blacklisted
    ]


async def get_assets_endpoint():
    assets = await asset_dal.get_assets_list()
    assets.sort(key=lambda asset: asset.symbol)
    return [
        WalletAssetExport.from_asset_dao(asset)
        for asset in assets
        if (
            not asset.blacklisted
            and not asset.community
            and not asset.deprecated
        )
        or (
            asset.contract_address
            in {
                config.ton.tgr_contract_address,
                config.ton.fnz_contract_address,
                config.ton.scale_contract_address,
            }
        )
    ]
