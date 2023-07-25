from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN: str
    ADMINS: list[int]


class CommissionSchema(BaseModel):
    COMMISSION_BUY: int
    COMMISSION_SALES: int
    MIN_BYN: int
    MIN_RUB: int


class ConfigSchema(BaseModel):
    BOT: BotSchema
    DATABASE: str
    CAPTCHA: str

    COMMISSION: CommissionSchema
    PAYMENT_TIMER: int
