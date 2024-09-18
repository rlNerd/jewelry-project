from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from dotenv import load_dotenv
import os

load_dotenv()
engine = create_async_engine(url=os.getenv('DB'))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    surname: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[int] = mapped_column(nullable=False) # 0 - user, 1 - admin


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(35), nullable=False)
    description: Mapped[str] = mapped_column(Text,nullable=True)
    price: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    image: Mapped[str] = mapped_column(String(150), nullable=False)


class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25),nullable=False)
    description: Mapped[str] = mapped_column(Text,nullable=True)
    image: Mapped[str] = mapped_column(String(150), nullable=False)


class Busket(Base):
    __tablename__ = 'busket'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.tg_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped['User'] = relationship(backref='busket')
    product: Mapped['Product'] = relationship(backref='busket')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)