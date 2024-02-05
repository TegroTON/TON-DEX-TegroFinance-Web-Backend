from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

from src.utils.camel_to_snake import camel_to_snake


@as_declarative()
class Base(AsyncAttrs):
    __name__: str

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)
