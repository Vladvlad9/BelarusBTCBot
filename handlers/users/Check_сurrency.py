import re

from handlers.users.Cryptocurrency import Cryptocurrency
from states.users.userStates import UserStates


class Check_currency():
    def __init__(self, amount, abbreviation, exchange_type, buy, currency, coin):
        self.buy = buy
        self.currency = currency,
        self.coin = coin
        self.amount = amount
        self.abbreviation = abbreviation
        self.exchange_type = exchange_type

    async def get_text_Buy(self, integerNumber: bool = False, state=None):
        if self.exchange_type == "sell":
            if integerNumber:
                byn = await Cryptocurrency.get_byn()
                price_BTC: float = await Cryptocurrency.get_btc()
                get_buy: float = round(price_BTC * byn, 3)

                get_BYN_Btc: float = round(float(self.amount) / float(get_buy),2)
                await state.update_data(amount=float(get_BYN_Btc))
                await state.update_data(buy=self.amount)

                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                       f"{round(get_BYN_Btc, 2)} {self.coin}"
                await UserStates.ERIP.set()
                return text
                pass
            else:
                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                       f"{self.buy} {self.currency[0]}"
                await UserStates.ERIP.set()
                return text
        else:
            if integerNumber:
                byn = await Cryptocurrency.get_byn()
                price_BTC: float = await Cryptocurrency.get_btc()
                get_buy: float = round(price_BTC * byn, 3)

                get_BYN_Btc: float = round(float(self.amount) / float(get_buy), 2)
                await state.update_data(amount=float(get_BYN_Btc))
                await state.update_data(buy=self.amount)

                text = f"Сумма к получению: {round(get_BYN_Btc, 2)} {self.coin}\n" \
                       f"Сумма к оплате: {self.amount} {self.currency[0]}\n\n" \
                       f"📝Введите {self.coin}-адрес кошелька," \
                       f"куда вы хотите отправить " \
                       f"{round(get_BYN_Btc, 2)} {self.coin}"

                await UserStates.Wallet.set()
                return text
            else:
                text = f"Сумма к получению: {self.amount} {self.abbreviation}\n" \
                       f"Сумма к оплате: {round(self.buy, 2)} {self.currency[0]}\n\n" \
                       f"📝Введите {self.coin}-адрес кошелька," \
                       f"куда вы хотите отправить " \
                       f"{self.amount} {self.abbreviation}"
                await UserStates.Wallet.set()
            return text

    @staticmethod
    async def commaToDot(amount):
        count = amount.count(",")
        if count > 0:
            amount = re.sub(r",", ".", amount)
        else:
            amount = amount

        return amount
