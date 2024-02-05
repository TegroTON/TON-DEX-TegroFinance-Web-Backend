from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .transaction import TransactionDao


class AccountDao(Base):
    username: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    affiliate_id: Mapped[str] = mapped_column(
        BigInteger, ForeignKey("account_dao.id"), nullable=True
    )

    referrals: Mapped[List["AccountDao"]] = relationship(
        back_populates="affiliate",
        cascade="save-update",
    )
    affiliate: Mapped["AccountDao"] = relationship(
        remote_side="AccountDao.id",
        back_populates="referrals",
        cascade="save-update",
    )
    transactions: Mapped["TransactionDao"] = relationship(
        back_populates="account",
        cascade="save-update",
    )


class TonProofPayloadDao(Base):
    payload: Mapped[str] = mapped_column(String, nullable=False)
    ttl: Mapped[int] = mapped_column(BigInteger, nullable=False)
