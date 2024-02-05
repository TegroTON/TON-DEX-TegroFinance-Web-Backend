from typing import Any, Dict, List
from ..models import AssetDao
from ..database import database
from sqlalchemy import select


async def get_asset_by_symbol(symbol: str) -> AssetDao:
    async with database.create_session() as session:
        result = await session.execute(
            select(AssetDao).where(AssetDao.symbol == symbol)
        )

        return result.scalars().first()


async def get_asset_by_contract_address(contract_address: str) -> AssetDao:
    async with database.create_session() as session:
        result = await session.execute(
            select(AssetDao).where(
                AssetDao.contract_address == contract_address
            )
        )

        return result.scalars().first()


async def get_assets_list() -> List[AssetDao]:
    async with database.create_session() as session:
        result = await session.execute(select(AssetDao))

    return result.scalars().all()


async def get_assets_dict_key_contract_address() -> Dict[str, Any]:
    assets_list = await get_assets_list()

    assets_dict = {asset.contract_address: asset for asset in assets_list}

    return assets_dict


async def get_assets_dict_key_symbol() -> Dict[str, Any]:
    assets_list = await get_assets_list()

    assets_dict = {asset.symbol: asset for asset in assets_list}

    return assets_dict
