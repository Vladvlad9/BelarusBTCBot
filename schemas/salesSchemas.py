from datetime import datetime
from pydantic import BaseModel, Field, validator


class SalesSchema(BaseModel):
    user_id: int = Field(ge=1)
    sale_id: int = Field(default=None)
    currency: str
    quantity: float
    coin: str
    price_per_unit: float
    erip: str
    commission: str
    moneyDifference: float = Field(default=0)
    date = Field(default=datetime.now())
    status: bool = Field(default=False)


class SalesInDBSchema(SalesSchema):
    id: int = Field(ge=1)

