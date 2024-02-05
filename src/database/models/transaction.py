from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .account import AccountDao


class TransactionDao(Base):
    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("account_dao.id"), nullable=False
    )
    router_address: Mapped[str] = mapped_column(String, nullable=False)
    user_wallet_address: Mapped[str] = mapped_column(String, nullable=False)
    offer_jetton_address: Mapped[str] = mapped_column(String, nullable=False)
    offer_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ask_jetton_address: Mapped[str] = mapped_column(String, nullable=False)
    min_ask_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    forward_gas_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    query_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, autoincrement=True
    )
    referral_address: Mapped[str] = mapped_column(String, nullable=True)
    is_confirmed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    valid_until: Mapped[int] = mapped_column(BigInteger, nullable=False)

    account: Mapped["AccountDao"] = relationship(back_populates="transactions")
