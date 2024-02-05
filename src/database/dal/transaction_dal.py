import time
from random import randint
from typing import List

from sqlalchemy import select, update

from ..database import database
from ..models import TransactionDao


async def get_last_transaction_id() -> int:
    async with database.create_session() as session:
        result = await session.execute(
            select(TransactionDao.id)
            .order_by(TransactionDao.id.desc())
            .limit(1)
        )

    last_id = result.scalars().first() or 0
    return last_id


async def create_transaction(
    account_id: int,
    router_address: str,
    user_wallet_address: str,
    offer_jetton_address: str,
    offer_amount: int,
    ask_jetton_address: str,
    min_ask_amount: int,
    forward_gas_amount: int,
    referral_address: str,
    valid_until: int,
) -> int:
    last_id = await get_last_transaction_id()

    query_id = int(f"{account_id}{last_id + 1}") + randint(
        10000, 99999
    )  # TODO: think

    if not forward_gas_amount:
        forward_gas_amount = 0.3

    transaction = TransactionDao(
        account_id=account_id,
        router_address=router_address,
        user_wallet_address=user_wallet_address,
        offer_jetton_address=offer_jetton_address,
        offer_amount=offer_amount,
        ask_jetton_address=ask_jetton_address,
        min_ask_amount=min_ask_amount,
        forward_gas_amount=forward_gas_amount,
        referral_address=referral_address,
        query_id=query_id,
        valid_until=valid_until,
    )

    async with database.create_session() as session:
        session.add(transaction)
        await session.commit()

    return query_id


async def get_transaction_by_query_id(query_id: str) -> TransactionDao:
    query = select(TransactionDao).where(TransactionDao.queryId == query_id)

    async with database.create_session() as session:
        result = await session.execute(query)

    return result.scalars().first()


async def get_unconfirmed_swap_transactions() -> List[TransactionDao]:
    query = (
        select(TransactionDao)
        .where(TransactionDao.is_confirmed == False)  # noqa
        .where(TransactionDao.valid_until > int(time.time()) - 60 * 10)
    )

    async with database.create_session() as session:
        result = await session.execute(query)

    return result.scalars().all()


async def get_confirmed_transactions_for_user(
    user_wallet_address: str,
) -> List[TransactionDao]:
    query = (
        select(TransactionDao)
        .where(TransactionDao.user_wallet_address == user_wallet_address)
        .where(TransactionDao.is_confirmed == True)  # noqa
    )

    async with database.create_session() as session:
        result = await session.execute(query)

    return result.scalars().all()


async def set_transaction_confirmed(transaction_id: int):
    query = (
        update(TransactionDao)
        .where(TransactionDao.id == transaction_id)
        .values(is_confirmed=True)
    )

    async with database.create_session() as session:
        await session.execute(query)
        await session.commit()
