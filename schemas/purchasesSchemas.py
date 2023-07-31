from datetime import datetime
from pydantic import BaseModel, Field, validator


class PurchasesSchema(BaseModel):
    purchase_id: int = Field(default=None)
    user_id: int = Field(ge=1)
    currency: str
    quantity: float
    coin: str
    price_per_unit: float
    wallet: str
    date = Field(default=datetime.now())
    status: bool = Field(default=False)


class PurchasesInDBSchema(PurchasesSchema):
    id: int = Field(ge=1)

