from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, SmallInteger, \
    Float, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, validates

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    date_created = Column(TIMESTAMP, default=datetime.now())  # Дата создания акк.
    transaction_timer = Column(Boolean, default=False)
    captcha = Column(Text, default=False)
    check_captcha = Column(Boolean, default=False)


class Purchases(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    purchase_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    currency = Column(String(10))  # Валюта
    quantity = Column(Float)  # Количество
    coin = Column(String(10))
    price_per_unit = Column(Float)  # Цена за единицу
    date = Column(TIMESTAMP, default=datetime.now())  # Дата транзакции
    wallet = Column(Text, default=None)
    commission = Column(String, default=None)
    moneydifference = Column(Float)
    status = Column(Boolean, default=False)  # Статус

    user = relationship('Users', backref='purchases')


class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    sale_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    currency = Column(String(10))
    quantity = Column(Float)
    coin = Column(String(10))
    price_per_unit = Column(Float)
    date = Column(TIMESTAMP, default=datetime.now())
    erip = Column(String(11), default=None)
    commission = Column(String, default=None)
    moneydifference = Column(Float)
    status = Column(Boolean, default=False)

    user = relationship('Users', backref='sales')


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'))
    sale_id = Column(Integer, ForeignKey('sales.id'))
    date = Column(TIMESTAMP, default=datetime.now())
    status = Column(Boolean, default=False)

    purchase = relationship('Purchases', backref='transactions')
    sale = relationship('Sales', backref='transactions')

    __table_args__ = (
        UniqueConstraint('purchase_id', 'sale_id'),
    )


