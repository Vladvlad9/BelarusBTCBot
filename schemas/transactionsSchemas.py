from datetime import datetime
from pydantic import BaseModel, Field, validator


class TransactionsSchema(BaseModel):
    purchase_id: int = Field(default=None)
    sale_id: int = Field(default=None)
    date_created:  datetime = Field(default=datetime.now())
    status: bool = Field(default=False)

    @validator('user_id')
    def validate_user_id(cls, value):
        if value is None or value <= 0:
            raise ValueError('User ID must be a positive integer.')
        return value

    @validator('date')
    def validate_date(cls, value):
        if value is None or not isinstance(value, datetime):
            raise ValueError('Date must be a datetime object.')
        return value


class TransactionsInDBSchema(TransactionsSchema):
    id: int = Field(ge=1)

    @validator('id')
    def validate_id(cls, value):
        if value is None or value <= 0:
            raise ValueError('ID must be a positive integer.')
        return value