from datetime import datetime
from pydantic import BaseModel, Field, validator


class PurchasesSchema(BaseModel):
    purchase_id: int
    user_id: int = Field(ge=1)
    currency: str
    quantity: float
    coin: str
    price_per_unit: float
    wallet: str
    date = Field(default=datetime.now())
    status: bool = Field(default=False)
    #
    # @validator('price_per_unit')
    # def validate_price_per_unit(cls, value):
    #     if value < 0:
    #         raise ValueError('Price per unit must be greater than or equal to 0.')
    #     return value


class PurchasesInDBSchema(PurchasesSchema):
    id: int = Field(ge=1)

