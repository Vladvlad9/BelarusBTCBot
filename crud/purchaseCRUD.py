from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Purchases, create_async_session
from schemas import PurchasesSchema, PurchasesInDBSchema


class CRUDPurchases(object):

    @staticmethod
    @create_async_session
    async def add(purchase: PurchasesSchema, session: AsyncSession = None) -> PurchasesInDBSchema | None:
        purchases = Purchases(
            **purchase.dict()
        )
        session.add(purchases)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(purchases)
            return PurchasesInDBSchema(**purchases.__dict__)

    @staticmethod
    @create_async_session
    async def delete(purchase_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Purchases)
            .where(Purchases.id == purchase_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(id: int = None,
                  session: AsyncSession = None) -> PurchasesInDBSchema | None:
        purchases = await session.execute(
            select(Purchases)
            .where(Purchases.id == id).order_by(Purchases.id)
        )
        if purchase := purchases.first():
            return PurchasesInDBSchema(**purchase[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[PurchasesInDBSchema]:
        try:
            purchases = await session.execute(
                select(Purchases)
                .order_by(Purchases.id)
            )
            return [PurchasesInDBSchema(**purchase[0].__dict__) for purchase in purchases]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(purchase: PurchasesInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Purchases)
            .where(Purchases.id == purchase.id)
            .values(**purchase.dict())
        )
        await session.commit()
