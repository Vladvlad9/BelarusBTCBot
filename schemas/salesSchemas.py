from datetime import datetime
from pydantic import BaseModel, Field, validator


class SalesSchema(BaseModel):
    user_id: int = Field(ge=1)
    currency: str
    quantity: int
    coin: str
    price_per_unit: float
    wallet: str
    erip: str
    date = Field(default=datetime.now())
    status: bool = Field(default=False)


class SalesInDBSchema(SalesSchema):
    id: int = Field(ge=1)

