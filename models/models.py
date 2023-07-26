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


class Purchases(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    currency = Column(String(10))  # Валюта
    quantity = Column(Integer)  # Количество
    coin = Column(String(10))
    price_per_unit = Column(Float)  # Цена за единицу
    date = Column(TIMESTAMP, default=datetime.now())  # Дата транзакции
    wallet = Column(Text, default=None)
    erip = Column(String(11), default=None)
    status = Column(Boolean, default=False)  # Статус

    user = relationship('Users', backref='purchases')


class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    currency = Column(String(10))
    quantity = Column(Integer)
    coin = Column(String(10))
    price_per_unit = Column(Float)
    date = Column(TIMESTAMP, default=datetime.now())
    wallet = Column(Text, default=None)
    erip = Column(String(11), default=None)
    status = Column(Boolean, default=False)

    def __init__(self, user_id, currency, quantity, coin, price_per_unit, date, status, wallet, erip):
        super().__init__(user_id, currency, quantity, coin, price_per_unit, date, status, wallet, erip)

    @validates('erip')
    def validate_quantity(self, key, value):
        if value < 11:
            raise ValueError('erip field must not be < 11')
        return value

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


