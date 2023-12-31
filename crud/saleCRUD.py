import logging

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Sales, create_async_session
from schemas import SalesSchema, SalesInDBSchema


class CRUDSales(object):

    @staticmethod
    @create_async_session
    async def add(sale: SalesSchema, session: AsyncSession = None) -> SalesInDBSchema | None:
        sales = Sales(
            **sale.dict()
        )
        session.add(sales)
        try:
            await session.commit()
        except IntegrityError as e:
            logging.error(f'Error add sale in db: {e}')
        else:
            await session.refresh(sales)
            return SalesInDBSchema(**sales.__dict__)

    @staticmethod
    @create_async_session
    async def delete(sale_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Sales)
            .where(Sales.id == sale_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(id: int = None,
                  sale_id: int = None,
                  session: AsyncSession = None) -> SalesInDBSchema | None:
        if sale_id:
            sales = await session.execute(
                select(Sales).where(Sales.sale_id == sale_id)
            )
        else:
            sales = await session.execute(
                select(Sales).where(Sales.id == id)
            )
        if sale := sales.first():
            return SalesInDBSchema(**sale[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(user_id: int = None, session: AsyncSession = None) -> list[SalesInDBSchema]:
        try:
            if user_id:
                sales = await session.execute(
                    select(Sales)
                    .where(Sales.user_id == user_id)
                )
            else:
                sales = await session.execute(
                    select(Sales)
                )
            return [SalesInDBSchema(**sale[0].__dict__) for sale in sales]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(sale: SalesInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Sales)
            .where(Sales.id == sale.id)
            .values(**sale.dict())
        )
        await session.commit()
