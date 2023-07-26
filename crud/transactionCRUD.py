import logging

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Transactions, create_async_session
from schemas import TransactionsSchema, TransactionsInDBSchema


class CRUDTransactions(object):

    @staticmethod
    @create_async_session
    async def add(transaction: TransactionsSchema, session: AsyncSession = None) -> TransactionsInDBSchema | None:
        transactions = Transactions(
            **transaction.dict()
        )
        session.add(transactions)
        try:
            await session.commit()
        except IntegrityError as e:
            logging.error(f'Error add transaction in db: {e}')
        else:
            await session.refresh(transactions)
            return TransactionsInDBSchema(**transactions.__dict__)

    @staticmethod
    @create_async_session
    async def delete(transaction_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Transactions)
            .where(Transactions.id == transaction_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(transaction_id: int = None,
                  id: int = None,
                  session: AsyncSession = None) -> TransactionsInDBSchema | None:
        if transaction_id:
            transactions = await session.execute(
                select(Transactions)
                .where(Transactions.user_id == transaction_id).order_by(Transactions.id)
            )  # нужно глянуть
        else:
            transactions = await session.execute(
                select(Transactions)
                .where(Transactions.id == id).order_by(Transactions.id)
            )
        if transaction := transactions.first():
            return TransactionsInDBSchema(**transaction[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[TransactionsInDBSchema]:
        try:
            transactions = await session.execute(
                select(Transactions)
                .order_by(Transactions.id)
            )
            return [TransactionsInDBSchema(**transaction[0].__dict__) for transaction in transactions]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(transaction: TransactionsInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Transactions)
            .where(Transactions.id == transaction.id)
            .values(**transaction.dict())
        )
        await session.commit()
