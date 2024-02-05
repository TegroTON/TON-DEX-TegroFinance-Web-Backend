from typing import List
from ..models.dex import PoolDao
from ..database import database
from sqlalchemy import and_, or_, select


async def get_pools(include_deprecated: bool = False) -> List[PoolDao]:
    query = select(PoolDao)

    if not include_deprecated:
        query = query.where(PoolDao.deprecated == False)  # noqa

    async with database.create_session() as session:
        result = await session.execute(query)

    return result.scalars().all()


async def get_pool_by_address(address: str) -> PoolDao:
    async with database.create_session() as session:
        result = await session.execute(
            select(PoolDao).where(PoolDao.address == address)
        )

    return result.scalars().first()


async def get_pool_for_assets(
    token0_address: str,
    token1_address: str,
) -> PoolDao:
    async with database.create_session() as session:
        result = await session.execute(
            select(PoolDao).where(
                or_(
                    and_(
                        PoolDao.token0_address == token0_address,
                        PoolDao.token1_address == token1_address,
                    ),
                    and_(
                        PoolDao.token0_address == token1_address,
                        PoolDao.token1_address == token0_address,
                    ),
                )
            )
        )

    return result.scalars().first()
