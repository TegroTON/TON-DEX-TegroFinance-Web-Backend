from ..models import TonProofPayloadDao, AccountDao
from ..database import database
from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def get_account(user_address: str) -> AccountDao | None:
    # print(user_address)
    query = (
        select(AccountDao)
        .where(AccountDao.address == user_address)
        .options(joinedload(AccountDao.affiliate, AccountDao.referrals))
    )
    async with database.create_session() as session:
        result = await session.execute(query)

        account = result.scalar()

    return account


async def create_account(
    user_address: str,
    affiliate_address: str,
) -> AccountDao:
    async with database.create_session() as session:
        affiliate_account_id = None
        if affiliate_address:
            affiliate_account = await get_account(affiliate_address)
            affiliate_account_id = affiliate_account.id

        account = AccountDao(
            address=user_address,
            affiliate_id=affiliate_account_id,
        )

        session.add(account)
        await session.commit()

    return account


async def save_ton_proof_payload(
    payload: str,
    ttl: int,
) -> TonProofPayloadDao:
    async with database.create_session() as session:
        ton_proof_payload = TonProofPayloadDao(
            payload=payload,
            ttl=ttl,
        )

        session.add(ton_proof_payload)
        await session.commit()

    return ton_proof_payload


async def get_ton_proof_payload(
    payload: str,
) -> TonProofPayloadDao | None:
    async with database.create_session() as session:
        result = await session.execute(
            select(TonProofPayloadDao).where(
                TonProofPayloadDao.payload == payload
            )
        )

        ton_proof_payload = result.scalar()

    return ton_proof_payload
