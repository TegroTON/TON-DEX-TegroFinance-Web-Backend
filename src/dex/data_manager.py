from src.database import database
from src.database.dal import asset_dal, pool_dal, transaction_dal
from src.database.models import AssetDao, PoolDao

from .http_api import get_assets, get_pools, update_swap_transaction


async def update_assets():
    try:
        assets = await get_assets()
    except Exception:
        return

    for new_asset_data in assets.asset_list:
        try:
            async with database.create_session() as session:
                asset_data = await asset_dal.get_asset_by_contract_address(
                    new_asset_data.contract_address
                )

                if asset_data:
                    asset_data.update(**new_asset_data.model_dump())
                else:
                    asset_data = AssetDao.from_dict(
                        new_asset_data.model_dump(
                            exclude=["balance", "wallet_address"],
                        )
                    )
                    session.add(asset_data)

                await session.commit()
        except Exception:
            # print(e)
            continue


async def update_pools():
    try:
        new_pools = await get_pools()
    except Exception:
        return

    pools = await pool_dal.get_pools(include_deprecated=True)
    pools_dict = {pool.address: pool for pool in pools}

    for new_pool_data in new_pools.pool_list:
        try:
            pool_data = pools_dict.get(new_pool_data.address, None)

            if not pool_data:
                pool_data = PoolDao.from_dict(
                    {
                        **new_pool_data.model_dump(),
                    }
                )
            else:
                pool_data.update(**new_pool_data.model_dump())

            async with database.create_session() as session:
                session.add(pool_data)
                await session.commit()
        except Exception:
            pass


async def update_swap_transactions():
    transactions = await transaction_dal.get_unconfirmed_swap_transactions()

    for transaction in transactions:
        await update_swap_transaction(transaction)
