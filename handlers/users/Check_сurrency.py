import re

from config import CONFIG
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

                get_BYN_Btc: float = round(float(self.amount) / float(get_buy), 2)
                await state.update_data(amount=float(get_BYN_Btc))
                await state.update_data(buy=self.amount)

                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                       f"{round(get_BYN_Btc, 2)} {self.coin}\n\n" \
                       f"Сумма к <b>продаже</b> <code>{self.amount}</code> {self.coin}\n" \
                       f"я тут"
                await UserStates.ERIP.set()
                return text
            else:
                # потом изменю!
                newPrice = round(self.buy * float(CONFIG.COMMISSION.COMMISSION_SALES), 2)
                moneyDifference = round(newPrice - self.buy, 2)
                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                       f"{round(self.buy * float(CONFIG.COMMISSION.COMMISSION_SALES), 2)} {self.currency[0]}\n\n" \
                       f"Сумма к <b>продаже</b> <code>{self.amount}</code> {self.coin}"
                await state.update_data(moneyDifference=moneyDifference)
                await state.update_data(buy=self.buy * float(CONFIG.COMMISSION.COMMISSION_SALES))
                await UserStates.ERIP.set()
                return text
        else:
            if integerNumber:
                byn = await Cryptocurrency.get_byn()
                price_BTC: float = await Cryptocurrency.get_btc()
                get_buy: float = round(price_BTC * byn, 3)

                if self.coin == "Bitcoin":
                    getUSD = round(float(self.amount) / byn, 3)  # Получаем доллары
                    get_BYN_Btc = round(getUSD / (price_BTC * float(CONFIG.COMMISSION.COMMISSION_BUY)), 8)# тут 8 цифр
                    moneyDifference: float = round(float(self.amount) - (float(get_BYN_Btc) * float(get_buy)), 2)
                    text = f"Сумма к получению: {get_BYN_Btc} {self.coin}\n" \
                           f"Сумма к оплате: {self.amount} {self.currency[0]}"

                    text_two = f"📝Введите {self.coin}-адрес кошелька," \
                               f"куда вы хотите отправить " \
                               f"{get_BYN_Btc} {self.coin}"

                    await state.update_data(amount=float(get_BYN_Btc))
                    await state.update_data(moneyDifference=moneyDifference)
                    await state.update_data(buy=self.amount)

                else:
                    get_BYN_Btc = round(float(self.amount) * (byn * float(CONFIG.COMMISSION.COMMISSION_BUY)), 3)

                    text = f"Сумма к получению: {self.amount} {self.coin}\n" \
                           f"Сумма к оплате: {get_BYN_Btc} {self.currency[0]}"

                    text_two = f"📝Введите {self.coin}-адрес кошелька," \
                               f"куда вы хотите отправить " \
                               f"{self.amount} {self.coin}"

                    await state.update_data(amount=self.amount)
                    await state.update_data(buy=float(get_BYN_Btc))

                await UserStates.Wallet.set()
                return [text, text_two]
            else:
                text = f"Сумма к получению: {self.amount} {self.abbreviation}\n" \
                       f"Сумма к оплате: {self.buy} {self.currency[0]}\n\n"
                text_two = f"📝Введите {self.coin}-адрес кошелька," \
                           f"куда вы хотите отправить " \
                           f"{self.amount} {self.abbreviation}"
                await UserStates.Wallet.set()
            return [text, text_two]

    @staticmethod
    async def commaToDot(amount):
        count = amount.count(",")
        if count > 0:
            amount = re.sub(r",", ".", amount)
        else:
            amount = amount

        return amount
