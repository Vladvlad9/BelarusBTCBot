from datetime import datetime
from pydantic import BaseModel, Field, validator


class SalesSchema(BaseModel):
    user_id: int = Field(ge=1)
    currency: str
    quantity: int
    coin: str
    wallet: str
    erip:str = Field(min_length=11, max_length=11, default=None)
    price_per_unit: float
    date = Field(default=datetime.now())
    status: bool = Field(default=False)

    @validator('quantity')
    def validate_quantity(cls, value):
        if value < 1:
            raise ValueError('Quantity must be greater than or equal to 1.')
        return value

    @validator('price_per_unit')
    def validate_price_per_unit(cls, value):
        if value < 0:
            raise ValueError('Price per unit must be greater than or equal to 0.')
        return value


class SalesInDBSchema(SalesSchema):
    id: int = Field(ge=1)

