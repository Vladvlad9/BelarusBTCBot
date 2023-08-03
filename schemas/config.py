from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN: str
    ADMINS: list[int]


class CommissionSchema(BaseModel):
    COMMISSION_BUY: str
    COMMISSION_SALES: str
    MIN_BYN: int
    MIN_RUB: int


class ConfigSchema(BaseModel):
    BOT: BotSchema
    DATABASE: str
    CAPTCHA: str

    COMMISSION: CommissionSchema
    PAYMENT_TIMER: int
