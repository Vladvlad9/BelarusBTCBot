from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(ge=1)
    date_created:  datetime = Field(default=datetime.now())
    transaction_timer: bool = Field(default=False)
    captcha: str


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
