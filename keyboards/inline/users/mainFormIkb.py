import asyncio
import logging
import re
from decimal import Decimal

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers
from crud.purchaseCRUD import CRUDPurchases
from crud.saleCRUD import CRUDSales
from crud.transactionCRUD import CRUDTransactions
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionsSchema, PurchasesSchema, SalesSchema
from states.users.userStates import UserStates

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForms:
    @staticmethod
    async def receipt(state, message) -> str:
        get_state_data = await state.get_data()

        if get_state_data['exchangeType'] == "buy":
            sell = f"<b>Продаете</b>: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n"
            get = f"💵<b>Получаете</b>: {get_state_data['amount']} {get_state_data['coin']}\n"
        else:
            sell = f"<b>Продаете</b>: {get_state_data['amount']} {get_state_data['coin']}\n"
            get = f"💵<b>Получаете</b>: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n"

        text = f"<b>✅Заявка №449112 успешно создана.</b>\n\n" \
               f"{sell}\n" \
               f"<b>ЕРИП реквизиты</b>: {get_state_data['erip']}\n\n" \
               f"Ваш ранг: 👶, скидка 0.0%\n\n" \
               f"{get}\n" \
               f"<b>Реквизиты для перевода {get_state_data['coin']}</b>:\n\n" \
               f"<code>{message.text}</code>\n\n" \
               f"⏳<b>Заявка действительна</b>: 15 минут\n\n" \
               f'☑️После успешного перевода денег по указанным реквизитам нажмите на кнопку ' \
               f'"<b>Я оплатил(а)</b>" или же вы можете отменить данную заявку, ' \
               f'нажав на кнопку "<b>Отменить заявку</b>".'

        return text

    @staticmethod
    async def receipt2(state, message) -> str:
        get_state_data = await state.get_data()

        text = f"<b>✅Заявка №449112 успешно создана.</b>\n\n" \
               f"💵<b>Получаете</b>: {get_state_data['amount']} {get_state_data['coin']}\n" \
               f"<b>{get_state_data['coin']}-адрес</b>:\n\n" \
               f"<code>{message.text}</code>\n\n" \
               f"Ваш ранг: 👶, скидка 0.0%\n\n" \
               f"💵Сумма к оплате: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n" \
               f"Резквизиты для оплаты:\n\n" \
               f"- ЕРИП ПЛАТЕЖИ\n" \
               f"- БАНКОВСКИЕ ФИНАНСОВЫЕ УСЛУГИ\n" \
               f"- БАНКИ НКФО\n" \
               f"- БАНК ДАБРАБЫТ\n" \
               f"- ПОПОЛН. СЧЕТА ПО НОМ.КАРТЫ\n" \
               f"- 14276766\n\n" \
               f"⏳Заявка действительна: 15 минут\n\n" \
               f'☑️После успешного перевода денег по указанным реквизитам нажмите на кнопку ' \
               f'"<b>Я оплатил(а)</b>" или же вы можете отменить данную заявку, ' \
               f'нажав на кнопку "<b>Отменить заявку</b>".'

        # if get_state_data['exchangeType'] == "buy":
        #     sell = f"<b>Продаете</b>: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n"
        #     get = f"💵<b>Получаете</b>: {get_state_data['amount']} {get_state_data['coin']}\n"
        # else:
        #     sell = f"<b>Продаете</b>: {get_state_data['amount']} {get_state_data['coin']}\n"
        #     get = f"💵<b>Получаете</b>: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n"
        #
        # text = f"<b>✅Заявка №449112 успешно создана.</b>\n\n" \
        #        f"{sell}\n" \
        #        f"<b>ЕРИП реквизиты</b>: {get_state_data['erip']}\n\n" \
        #        f"Ваш ранг: 👶, скидка 0.0%\n\n" \
        #        f"{get}\n" \
        #        f"<b>Реквизиты для перевода {get_state_data['coin']}</b>:\n\n" \
        #        f"<code>{message.text}</code>\n\n" \
        #        f"⏳<b>Заявка действительна</b>: 15 минут\n\n" \
        #        f'☑️После успешного перевода денег по указанным реквизитам нажмите на кнопку ' \
        #        f'"<b>Я оплатил(а)</b>" или же вы можете отменить данную заявку, ' \
        #        f'нажав на кнопку "<b>Отменить заявку</b>".'

        return text

    @staticmethod
    async def messageAdministrators(message, state, photo):
        state_data = await state.get_data()
        text = f"Заявка № {1}\n\n" \
               f"Имя {message.from_user.first_name}\n" \
               f"Получено {state_data['currency_abbreviation']}: {state_data['buy']}\n" \
               f"Нужно отправить  {state_data['coin']}: {state_data['amount']}\n"

        tasks = []
        for admin in CONFIG.BOT.ADMINS:
            tasks.append(bot.send_photo(chat_id=admin, photo=photo,
                                        caption=f"Пользователь оплатил!\n\n"
                                                f"{text}"))
        await asyncio.gather(*tasks, return_exceptions=True)  # Отправка всем админам сразу
        await MainForms.confirmation_timer(message=message)

    @staticmethod
    async def confirmation_timer(message):
        await asyncio.sleep(3)
        await message.answer(text="Заявка успешно создана",
                             reply_markup=await MainForms.main_ikb())

    @staticmethod
    async def abbreviation(coin: str):
        data = {
            "Bitcoin": "btc",
            "Litecoin": "ltc",
            "USDT(trc20)": "usdt",
            "Monero(XMR)": "xmr",
            "RUB": "₽",
            "BYN": "Br",
        }
        if coin in data:
            return data[coin]

    @staticmethod
    async def buy(coin: str, currency: str, amount: str):
        if currency == "RUB":
            rub = await Cryptocurrency.get_rub()
            if coin == "Bitcoin":
                price_BTC: float = await Cryptocurrency.get_btc()
                buy: float = round(float(amount) * price_BTC * rub, 3)
                return buy

            elif coin == "Litecoin":
                get_ltc = await Cryptocurrency.get_ltc_to_rub()
                buy: float = round(float(amount) * get_ltc, 3)
                return buy

            elif coin == "USDT(trc20)":
                get_trc: float = await Cryptocurrency.get_trx()
                buy: float = round(float(amount) * get_trc * rub, 3)
                return buy

            elif coin == "Monero(XMR)":
                get_xmr: float = await Cryptocurrency.get_trx()
                buy: float = round(float(amount) * get_xmr * rub, 3)
                return buy

        elif currency == "BYN":
            byn = await Cryptocurrency.get_byn()
            if coin == "Bitcoin":
                price_BTC: float = await Cryptocurrency.get_btc()
                buy: float = round(float(amount) * price_BTC * byn, 3)
                return buy

            elif coin == "Litecoin":
                get_ltc: float = await Cryptocurrency.get_ltc()
                buy: float = round(float(amount) * get_ltc * byn, 3)
                return buy

            elif coin == "USDT(trc20)":
                get_trc: float = await Cryptocurrency.get_trx()
                buy: float = round(float(amount) * get_trc * byn, 3)
                return buy

            elif coin == "Monero(XMR)":
                get_xmr: float = await Cryptocurrency.get_xmr()
                buy: float = round(float(amount) * get_xmr * byn, 3)
                return buy

    @staticmethod
    async def buy_to_currency(coin: str, currency: str, amount: str):

        """
            This static method calculates the amount of a specific cryptocurrency that can be bought with a given amount
            of currency.

            Parameters:
            - coin (str): The name of the cryptocurrency.
            - currency (str): The currency to be used for the purchase.
            - amount (str): The amount of currency to be used for the purchase.

            Returns:
            buy (float): The amount of cryptocurrency that can be bought with the given amount of currency.

            Note:
            The method uses the `Cryptocurrency` class to fetch the current prices of the cryptocurrencies.

            Example:
            Suppose we want to buy Bitcoin (BTC) with 100 RUB. We can call the method as follows:

            result = await Cryptocurrency.buy_to_currency("Bitcoin", "RUB", "100")
            print(result)
            0.00123456

            The method will return the amount of Bitcoin that can be bought with 100 RUB, rounded to 8 decimal places.
            """

        if currency == "RUB":
            if coin == "Bitcoin":
                price_BTC = await Cryptocurrency.get_btc()
                return round(Decimal(amount) / Decimal(price_BTC), 3)

            elif coin == "Litecoin":
                get_ltc = await Cryptocurrency.get_ltc_to_rub()
                return round(Decimal(amount) / Decimal(get_ltc), 3)

            elif coin == "USDT(trc20)":
                get_trc = await Cryptocurrency.get_trx()
                return round(Decimal(amount) / Decimal(get_trc), 3)

            elif coin == "Monero(XMR)":
                get_xmr = await Cryptocurrency.get_trx()
                return round(Decimal(amount) / Decimal(get_xmr), 3)

        elif currency == "BYN":
            if coin == "Bitcoin":
                price_BTC: float = await Cryptocurrency.get_btc()
                return round(Decimal(amount) / Decimal(price_BTC), 8)

            elif coin == "Litecoin":
                get_ltc: float = await Cryptocurrency.get_ltc()
                return round(Decimal(amount) / Decimal(get_ltc), 8)

            elif coin == "USDT(trc20)":
                get_trc: float = await Cryptocurrency.get_trx()
                return round(Decimal(amount) / Decimal(get_trc), 8)

            elif coin == "Monero(XMR)":
                get_xmr: float = await Cryptocurrency.get_xmr()
                return round(Decimal(amount) / Decimal(get_xmr), 8)

    @staticmethod
    async def main_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Купить",
                                         callback_data=main_cb.new("Buy", "getBuy", 0, 0)),
                    InlineKeyboardButton(text="Продать",
                                         callback_data=main_cb.new("Sell", "getSell", 0, 0))
                ],
                [
                    InlineKeyboardButton(text="Контанкты",
                                         callback_data=main_cb.new("Contacts", "getContacts", 0, 0)),
                    InlineKeyboardButton(text="Розыгрыши", callback_data=main_cb.new("Raffles", "getRaffles", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def currency_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="BYN",
                                         callback_data=main_cb.new(target, action, "BYN", 0)),
                    InlineKeyboardButton(text="RUB",
                                         callback_data=main_cb.new(target, action, "RUB", 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("Main", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def coin_ikb(target: str, action: str) -> InlineKeyboardMarkup:

        data = {
            "Bitcoin": {"target": target, "action": action, "id": "Bitcoin", "editId": 0},
            "Litecoin": {"target": target, "action": action, "id": "Litecoin", "editId": 0},
            "USDT(trc20)": {"target": target, "action": action, "id": "USDT(trc20)", "editId": 0},
            "Monero(XMR)": {"target": target, "action": action, "id": "Monero(XMR)", "editId": 0},
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=name,
                                                         callback_data=main_cb.new(name_items["target"],
                                                                                   name_items["action"],
                                                                                   name_items["id"],
                                                                                   name_items["editId"])
                                                         )
                                ] for name, name_items in data.items()
                            ] + [
                                [
                                    InlineKeyboardButton(text="◀️ Назад",
                                                         callback_data=main_cb.new("Buy", "getBuy", 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def contacts_ikb() -> InlineKeyboardMarkup:
        data = {
            "Отзывы": {"target": "Profile", "url": "https://t.me/ulad_islau"},
            "Чат": {"target": "Profile", "url": "https://t.me/ulad_islau"},
            "Оператор": {"target": "Profile", "url": "https://t.me/ulad_islau"},
            "Оператор-ночь": {"target": "Profile", "url": "https://t.me/ulad_islau"},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=name,
                                                         url=name_items['url']
                                                         )
                                ] for name, name_items in data.items()
                            ] +
                            [
                                [
                                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("Main", 0, 0, 0))

                                ]

                            ]
        )

    @staticmethod
    async def raffles_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Лотерея",
                                         callback_data=main_cb.new("Raffles", "getLottery", 0, 0)),
                    InlineKeyboardButton(text="Рулетка",
                                         callback_data=main_cb.new("Raffles", "getRoulette", 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Main", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def confirmation_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Я оплатил(а)",
                                         callback_data=main_cb.new(target, action, 0, 0)),
                ],
                [
                    InlineKeyboardButton(text="Отменить заявку", callback_data=main_cb.new("Main", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def back_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def isfloat(value: str):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("main"):
                data = main_cb.parse(callback_data=callback.data)

                if data.get("target") == "Main":
                    await state.finish()
                    text = "🚀🚀🚀Название обменника🚀🚀🚀предлагает:\n\n" \
                           "✳️Гарантированную скорость зачисления на кошелек до 3️⃣0️⃣ минут 🚀\n" \
                           "✳️Выгодный курс на обмен👌\n" \
                           "✳️Работаем 2️⃣4️⃣⚡️7️⃣\n" \
                           "✳️Индивидуальный подход 🤗 и круглосуточная поддержка оператора 😎📲\n" \
                           "✳️Конфиденциальность 🔐\n" \
                           "Мы ценим Вас😜 и Ваше время🚀и гарантированную полную безопасность 🔐\n\n" \
                           "Наш бот🤖 -\n" \
                           "Наш оператор😎 -\n\n" \
                           "😎С уважением, Ваш 😎"
                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForms.main_ikb())

                elif data.get("target") == "Buy":
                    if data.get("action") == "getBuy":
                        text = "Выберите валюту."
                        await state.update_data(exchangeType="buy")
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.currency_ikb(
                                                             target='Buy',
                                                             action='currency_buy')
                                                         )

                    elif data.get("action") == "currency_buy":
                        await state.update_data(currency=data.get("id"))
                        await state.update_data(currency_abbreviation=await MainForms.abbreviation(data.get("id")))
                        text = "Выберите валюту которую вы хотите купить."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.coin_ikb(target="Buy",
                                                                                               action="coin_buy")
                                                         )

                    elif data.get('action') == "coin_buy":
                        coin_id = data.get('id')
                        await state.update_data(coin=coin_id)
                        text = f'✅ Введите нужную сумму в {coin_id} или в рублях\n' \
                               '🤖Оплата будет проверена автоматически.'

                        await UserStates.Buy.set()
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb("Buy", "currency_buy"))

                    elif data.get('action') == "confirmation_buy":
                        await callback.message.edit_text(text="📎 Отправьте скрин перевода, либо чек оплаты!")
                        await UserStates.UserPhoto.set()

                elif data.get("target") == "Sell":
                    if data.get("action") == "getSell":
                        text = "Выберите валюту."
                        await state.update_data(exchangeType="sell")
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.currency_ikb(
                                                             target='Sell',
                                                             action='currency_buy')
                                                         )

                    elif data.get("action") == "currency_buy":
                        await state.update_data(currency=data.get("id"))
                        await state.update_data(currency_abbreviation=await MainForms.abbreviation(data.get("id")))
                        text = "Выберите валюту которую вы хотите продать."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.coin_ikb(target="Sell",
                                                                                               action="coin_buy")
                                                         )

                    elif data.get('action') == "coin_buy":
                        coin_id = data.get('id')
                        await state.update_data(coin=coin_id)
                        text = f'✅ Введите нужную сумму в {coin_id} или в рублях\n' \
                               '🤖Оплата будет проверена автоматически.'

                        await UserStates.Buy.set()
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb(target="Sell",
                                                                                               action="currency_buy"))

                    elif data.get('action') == "confirmation_buy":
                        await callback.message.edit_text(text="📎 Отправьте скрин перевода, либо чек оплаты!")
                        await UserStates.UserPhoto.set()

                elif data.get("target") == "Contacts":
                    if data.get("action") == "getContacts":
                        text = "Контакты"
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.contacts_ikb())

                elif data.get("target") == "Raffles":
                    if data.get("action") == "getRaffles":
                        text = "Розыгрыши от сервиса😈"
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.raffles_ikb())

        if message:
            await message.delete()

            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=message.message_id - 1
                )
            except BadRequest:
                pass

            if state:
                # if await state.get_state() == "UserStates:Buy":
                #     await state.update_data(amount=message.text)
                #     get_state_data = await state.get_data()
                #     abbreviation = await MainForms.abbreviation(get_state_data['coin'])
                #
                #     if get_state_data['currency'] == "RUB":
                #
                #         try:
                #             if len(message.text) < 3:
                #                 buy = await MainForms.buy(coin=get_state_data['coin'],
                #                                           currency=get_state_data['currency'],
                #                                           amount=get_state_data['amount'])
                #
                #                 text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                #                        f"{message.text} {abbreviation}"
                #
                #                 await state.update_data(buy=buy)
                #                 await message.answer(text=text,
                #                                      reply_markup=await MainForms.back_ikb(target="Main", action="0"),
                #                                      parse_mode="HTML")
                #                 await UserStates.ERIP.set()
                #
                #             elif message.text.find("0") != -1:
                #                 buy = await MainForms.buy(coin=get_state_data['coin'],
                #                                           currency=get_state_data['currency'],
                #                                           amount=get_state_data['amount'])
                #
                #                 text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                #                        f"{buy} {get_state_data['currency']}"
                #
                #                 await state.update_data(buy=buy)
                #                 await message.answer(text=text,
                #                                      reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #                 await UserStates.ERIP.set()
                #
                #             else:
                #                 buy = await MainForms.buy_to_currency(coin=get_state_data['coin'],
                #                                                       currency=get_state_data['currency'],
                #                                                       amount=get_state_data['amount'])
                #
                #                 text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                #                        f"{buy} {abbreviation}"
                #
                #                 await state.update_data(buy=buy)
                #                 await message.answer(text=text,
                #                                      reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #                 await UserStates.ERIP.set()
                #         except Exception as e:
                #             await message.answer(text="Не вверно введены данные",
                #                                  reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #             await UserStates.Buy.set()
                #             logging.error(f"Error {e}")
                #
                #     elif get_state_data['currency'] == 'BYN':
                #         try:
                #             if len(message.text) < 3:
                #                 buy = await MainForms.buy(coin=get_state_data['coin'],
                #                                           currency=get_state_data['currency'],
                #                                           amount=get_state_data['amount'])
                #
                #                 text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                #                        f"{message.text} {abbreviation}"
                #
                #                 await state.update_data(buy=buy)
                #                 await message.answer(text=text,
                #                                      reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #                 await UserStates.ERIP.set()
                #
                #             elif message.text.find("0") != -1:
                #                 buy = await MainForms.buy(coin=get_state_data['coin'],
                #                                           currency=get_state_data['currency'],
                #                                           amount=get_state_data['amount'])
                #
                #                 text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                #                        f"{buy} {get_state_data['currency']}"
                #
                #                 await state.update_data(buy=buy)
                #                 await message.answer(text=text,
                #                                      reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #                 await UserStates.ERIP.set()
                #
                #             else:
                #                 buy = await MainForms.buy_to_currency(coin=get_state_data['coin'],
                #                                                       currency=get_state_data['currency'],
                #                                                       amount=get_state_data['amount'])
                #
                #                 text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                #                        f"{buy} {abbreviation}"
                #
                #                 await state.update_data(buy=buy)
                #                 await message.answer(text=text,
                #                                      reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #                 await UserStates.ERIP.set()
                #         except Exception as e:
                #             await message.answer(text="Не вверно введена сумма\n"
                #                                       "Повторите попытку",
                #                                  reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                #             await UserStates.Buy.set()
                #             logging.error(f"Error {e}")

                if await state.get_state() == "UserStates:Buy":
                    await state.update_data(amount=message.text)
                    get_state_data = await state.get_data()
                    abbreviation = await MainForms.abbreviation(get_state_data['coin'])

                    try:
                        if len(message.text) < 3:
                            buy = await MainForms.buy(coin=get_state_data['coin'],
                                                      currency=get_state_data['currency'],
                                                      amount=get_state_data['amount'])

                            if get_state_data['exchangeType'] == "sell":
                                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                                       f"{buy} {get_state_data['currency']}" \
                                    if get_state_data['exchangeType'] == "sell" \
                                    else f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                                         f"{message.text} {abbreviation}"

                                await UserStates.ERIP.set()
                            else:
                                text = f"📝Введите {get_state_data['coin']}-адрес кошелька," \
                                       f"куда вы хотите отправить " \
                                       f"{get_state_data['amount']} {abbreviation}"
                                await message.answer(text=f"Сумма к получению: {get_state_data['amount']} "
                                                          f"{abbreviation}\n"
                                                          f"Сумма к оплате: {buy} "
                                                          f"{get_state_data['currency']}\n\n")

                                await UserStates.Wallet.set()

                        elif message.text.find("0") != -1:
                            buy = await MainForms.buy(coin=get_state_data['coin'],
                                                      currency=get_state_data['currency'],
                                                      amount=get_state_data['amount'])

                            if get_state_data['exchangeType'] == "sell":
                                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                                       f"{buy} {get_state_data['currency']}" \
                                    if get_state_data['exchangeType'] == "sell" \
                                    else f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                                         f"{buy} {get_state_data['currency']}"

                                await UserStates.ERIP.set()
                            else:
                                text = f"📝Введите {get_state_data['coin']}-адрес кошелька," \
                                       f"куда вы хотите отправить " \
                                       f"{get_state_data['amount']} {abbreviation}"
                                await message.answer(text=f"Сумма к получению: {get_state_data['amount']} "
                                                          f"{abbreviation}\n"
                                                          f"Сумма к оплате: {buy} "
                                                          f"{get_state_data['currency']}\n\n")

                                await UserStates.Wallet.set()

                            # text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                            #        f"{buy} {get_state_data['currency']}"

                        else:
                            buy = await MainForms.buy_to_currency(coin=get_state_data['coin'],
                                                                  currency=get_state_data['currency'],
                                                                  amount=get_state_data['amount'])

                            if get_state_data['exchangeType'] == "sell":
                                text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                                       f"{buy} {get_state_data['currency']}" \
                                    if get_state_data['exchangeType'] == "sell" \
                                    else f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить " \
                                         f"{buy} {abbreviation}"

                                await UserStates.ERIP.set()
                            else:
                                text = f"📝Введите {get_state_data['coin']}-адрес кошелька,"\
                                       f"куда вы хотите отправить "\
                                       f"{get_state_data['amount']} {abbreviation}"

                                await message.answer(text=f"Сумма к получению: {get_state_data['amount']} "
                                                          f"{abbreviation}\n"
                                                          f"Сумма к оплате: {buy} "
                                                          f"{get_state_data['currency']}\n\n")

                                await UserStates.Wallet.set()

                            # text = f"Введите <b>ЕРИП РБ</b> реквизиты, куда вы хотите получить {buy} {abbreviation}"

                        await state.update_data(buy=buy)
                        await message.answer(text=text,
                                             reply_markup=await MainForms.back_ikb(target="Main", action="0"),
                                             parse_mode="HTML")

                    except Exception as e:
                        await message.answer(text="Не вверно введены данные",
                                             reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                        await UserStates.Buy.set()
                        logging.error(f"Error {e}")

                elif await state.get_state() == "UserStates:ERIP":
                    if re.match(r"^[0-9]{11}$", message.text):
                        get_state_data = await state.get_data()
                        abbreviation = await MainForms.abbreviation(get_state_data['coin'])

                        # text = f"Сумма к получению: {get_state_data['amount']} {abbreviation}\n" \
                        #        f"Сумма к оплате: {get_state_data['buy']} {get_state_data['currency']}\n\n"

                        text = "✅Заявка №169916 успешно создана.\n\n" \
                               f"Продаете: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n" \
                               f"ЕРИП РБ реквизиты: <code>{message.text}</code>\n\n" \
                               "Ваш ранг: 👶, скидка 0.0%\n\n" \
                               f"💵Получаете: <code>{get_state_data['amount']} {get_state_data['coin']}</code>\n" \
                               f"Реквизиты для перевода {get_state_data['currency_abbreviation']}:\n\n" \
                               "<code>____________________</code>\n\n" \
                               "⏳Заявка действительна: 15 минут\n\n" \
                               '☑️После успешного перевода денег по указанному кошельку нажмите на кнопку ' \
                               '"Я оплатил(а)" или же вы можете отменить данную заявку, ' \
                               'нажав на кнопку "Отменить заявку".'

                        # await message.answer(text=text,
                        #                      reply_markup=await MainForms.back_ikb(target="Main",
                        #                                                            action="0"))

                        await message.answer(text=text,
                                             reply_markup=await MainForms.confirmation_ikb(target="Sell",
                                                                                           action="confirmation_buy"),
                                             parse_mode="HTML")

                        await state.update_data(erip=message.text)

                        # await UserStates.Wallet.set()
                    else:
                        text = "ЕРИП введен не верно\n" \
                               "Попробуйте ввести еще раз"
                        await message.answer(text=text,
                                             reply_markup=await MainForms.back_ikb(target="Main", action="0"))

                elif await state.get_state() == "UserStates:Wallet":
                    wallet = await Cryptocurrency.Check_Wallet(btc_address=message.text)
                    get_state_data = await state.get_data()
                    if wallet:
                        await state.update_data(wallet=message.text)
                        if get_state_data['exchangeType'] == "buy":
                            text = await MainForms.receipt2(state=state, message=message)

                        await message.answer(text=text,
                                             reply_markup=await MainForms.confirmation_ikb(target="Buy",
                                                                                           action="confirmation_buy"),
                                             parse_mode="HTML")
                    else:
                        text = f"Адрес кошелька <i>{message.text}</i> нету в blockchain\n" \
                               f"Введите еще раз адрес"
                        await message.answer(text=text, parse_mode="HTML",
                                             reply_markup=await MainForms.back_ikb(target="Main", action=""))

                elif await state.get_state() == "UserStates:UserPhoto":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await UserStates.UserPhoto.set()
                        else:
                            get_photo = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
                            photo = message.photo[0].file_id

                            try:
                                user = await CRUDUsers.get(user_id=message.from_user.id)
                                get_state_data = await state.get_data()

                                if get_state_data['exchangeType'] == "buy":
                                    purchase = await CRUDPurchases.add(purchase=PurchasesSchema(
                                        user_id=user.id,
                                        currency=get_state_data['currency'],
                                        quantity=get_state_data['amount'],
                                        coin=get_state_data['coin'],
                                        price_per_unit=get_state_data['buy'],
                                        wallet=get_state_data['wallet']
                                    ))
                                    transaction = await CRUDTransactions.add(transaction=TransactionsSchema(
                                        purchase_id=purchase.id
                                    ))

                                if get_state_data['exchangeType'] == "sell":
                                    sale = await CRUDSales.add(sale=SalesSchema(
                                        user_id=user.id,
                                        currency=get_state_data['currency'],
                                        quantity=get_state_data['amount'],
                                        coin=get_state_data['coin'],
                                        price_per_unit=get_state_data['buy'],
                                        erip=get_state_data['erip']
                                    ))
                                    transaction = await CRUDTransactions.add(transaction=TransactionsSchema(
                                        sale_id=sale.id
                                    ))
                            except Exception as e:
                                logging.error(f'Error add что происодит я хз in db: {e}')

                            try:
                                if transaction:
                                    await bot.download_file(file_path=get_photo.file_path,
                                                            destination=f'user_check/{1}_{message.from_user.id}.jpg',
                                                            timeout=12,
                                                            chunk_size=1215000)

                                    await MainForms.messageAdministrators(message=message, state=state, photo=photo)

                                    await state.finish()
                                else:
                                    await message.answer(text="Ошибка, попробуйте снова или "
                                                              "обратитесь к администраторам",
                                                         reply_markup=await MainForms.back_ikb(target="Main",
                                                                                               action=""))
                            except Exception as e:
                                logging.error(f'Error UserStates:UserPhoto: {e}')
