import asyncio
import logging
import random
import re
import string
from decimal import Decimal

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from config.config import CONFIGTEXT
from crud import CRUDUsers
from crud.purchaseCRUD import CRUDPurchases
from crud.saleCRUD import CRUDSales
from crud.transactionCRUD import CRUDTransactions
from handlers.users.Check_сurrency import Check_currency
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionsSchema, PurchasesSchema, SalesSchema
from states.users.userStates import UserStates

from PIL import ImageFont, ImageDraw, Image
main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForms:
    @staticmethod
    async def create_captcha(text: str) -> str:
        image = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('/opt/git/BelarusBTCBot/font/arial.ttf', size=30)
        # font = ImageFont.truetype('font/arial.ttf', size=30)
        draw.text((50, 25), text, font=font, fill='black')

        file_path = 'captcha.png'
        image.save(file_path)
        return file_path

    @staticmethod
    async def get_captcha() -> dict:
        captcha_text = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
        file_path = await MainForms.create_captcha(captcha_text)
        return {"captcha_text": captcha_text, "file_path": file_path}

    @staticmethod
    async def send_timer_message(chat_id: int, state):
        await state.finish()
        user = await CRUDUsers.get(user_id=chat_id)
        if user.transaction_timer:
            await asyncio.sleep(0)
            user.transaction_timer = False
            await CRUDUsers.update(user=user)
            await bot.send_message(chat_id=chat_id, text="Время вышло!")
            await bot.send_message(chat_id=chat_id,
                                   text=f'{CONFIGTEXT.MAIN_FORM.TEXT}',
                                   reply_markup=await MainForms.main_kb())
        else:
            await asyncio.sleep(0)
            user.transaction_timer = False
            await CRUDUsers.update(user=user)
            return

    @staticmethod
    async def main_kb() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            row_width=2,
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[
                [
                    KeyboardButton(text='Купить 💰'),
                    KeyboardButton(text='Продать 📈'),
                    KeyboardButton(text='Контакты 💬'),

                ]
            ]
        )

    @staticmethod
    async def receipt(state, message) -> str:
        get_state_data = await state.get_data()
        requisites = CONFIGTEXT.RequisitesBYN.TEXT

        text = f"<b>✅Заявка успешно создана.</b>\n\n" \
               f"💵<b>Получаете</b>: <u>{get_state_data['amount']}</u> <u>{get_state_data['coin']}</u>\n\n" \
               f"<b>{get_state_data['coin']}-адрес</b>:\n\n" \
               f"<code>{message.text}</code>\n\n" \
               f"💵<b>Сумма к оплате</b>: <u>{get_state_data['buy']}</u> <u>{get_state_data['currency_abbreviation']}</u>\n\n" \
               f"<b>Реквизиты для оплаты:</b>\n\n" \
               f"{requisites}" \
               f"\n⏳<b>Заявка действительна: <u>15 минут</u></b>\n\n" \
               f'☑️После успешного перевода денег по указанным реквизитам нажмите на кнопку ' \
               f'"<b>Я оплатил(а)</b>" или же вы можете отменить данную заявку, ' \
               f'нажав на кнопку "<b>Отменить заявку</b>".'

        return text

    @staticmethod
    async def messageAdministrators(message, state, photo, applicationNumber):
        state_data = await state.get_data()

        if state_data['exchangeType'] == "sell":
            text = f"Заявка № {applicationNumber}\n\n" \
                   f"Пользователь <code>{message.from_user.first_name}</code> хочет " \
                   f"<code>продать {state_data['amount']} {state_data['coin']}</code>\n\n" \
                   f"ЕРИП: <code>{state_data['erip']}</code>\n\n" \
                   f"Получите: {state_data['buy']} {state_data['currency_abbreviation']}\n\n"
        else:
            text = f"Заявка № {applicationNumber}\n\n" \
                   f"Имя: <code>{message.from_user.first_name}</code>\n" \
                   f"Получено: <code>{state_data['buy']} {state_data['currency_abbreviation']}</code>\n" \
                   f"Нужно отправить: <code>{state_data['amount']} {state_data['coin']}</code>\n" \
                   f"Кошелек: <code>{state_data['wallet']}</code>"

        tasks = []
        for admin in CONFIG.BOT.ADMINS:
            tasks.append(bot.send_photo(chat_id=admin, photo=photo,
                                        caption=f"Пользователь оплатил!⤴️\n\n"
                                                f"{text}"))
        await asyncio.gather(*tasks, return_exceptions=True)  # Отправка всем админам сразу
        await MainForms.confirmation_timer(message=message, applicationNumber=applicationNumber)

    @staticmethod
    async def confirmation_timer(message, applicationNumber):
        await message.answer(text=f"Заявка №<code>{applicationNumber}</code> успешно создана")
        await message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                             reply_markup=await MainForms.main_kb(),
                             parse_mode="HTML")

    @staticmethod
    async def abbreviation(coin: str):
        data = {
            "Bitcoin": "btc",
            "Litecoin": "ltc",
            "USDT": "usdt",
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

            elif coin == "USDT":
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

            elif coin == "USDT":
                get_trc: float = await Cryptocurrency.get_trx()
                buy: float = round(float(amount) * byn, 3)
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

            elif coin == "USDT":
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

            elif coin == "USDT":
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
                                         callback_data=main_cb.new("Buy", "currency_buy", 0, 0)),
                    InlineKeyboardButton(text="Продать",
                                         callback_data=main_cb.new("Sell", "currency_buy", 0, 0))
                ],
                [
                    InlineKeyboardButton(text="Контакты",
                                         callback_data=main_cb.new("Contacts", "getContacts", 0, 0))
                    # InlineKeyboardButton(text="Розыгрыши", callback_data=main_cb.new("Raffles", "getRaffles", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def currency_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="BYN",
                                         callback_data=main_cb.new(target, action, "BYN", 0))
                    # InlineKeyboardButton(text="RUB",
                    #                      callback_data=main_cb.new(target, action, "RUB", 0))
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
            "USDT(trc20)": {"target": target, "action": action, "id": "USDT", "editId": 0},
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
                                                         callback_data=main_cb.new("Main", "main", 0, 0))
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
                    InlineKeyboardButton(text="Отменить заявку", callback_data=main_cb.new("Main", "Captcha", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def back_ikb(target: str, action: str, coin_id: int = 0) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action, coin_id, 0))
                ]
            ]
        )

    @staticmethod
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("main"):
                data = main_cb.parse(callback_data=callback.data)

                if data.get("target") == "Main":
                    if data.get("action") == 'main':
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        user.transaction_timer = False
                        await CRUDUsers.update(user=user)
                        await state.finish()

                        await callback.message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                                                      reply_markup=await MainForms.main_kb())

                    elif data.get('action') == "Captcha":
                        captcha = await MainForms.get_captcha()

                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        user.check_captcha = False
                        user.transaction_timer = False
                        user.captcha = captcha['captcha_text']
                        await CRUDUsers.update(user=user)

                        await bot.send_photo(chat_id=callback.message.chat.id,
                                             photo=open(captcha["file_path"], 'rb'))

                        await bot.send_message(chat_id=callback.message.chat.id,
                                               text=CONFIGTEXT.FIRST_PAGE.TEXT)

                        await UserStates.Captcha.set()

                elif data.get("target") == "Buy":
                    if data.get("action") == "currency_buy":
                        await state.finish()
                        text = "Выберите валюту которую вы хотите купить."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.coin_ikb(target="Buy",
                                                                                               action="coin_buy")
                                                         )

                    elif data.get('action') == "coin_buy":
                        coin_id = data.get('id')

                        await state.update_data(exchangeType="buy")
                        await state.update_data(currency="BYN")
                        await state.update_data(currency_abbreviation="BYN")

                        await state.update_data(coin=coin_id)
                        addTxt = "USDT" if coin_id == "USDT" else "рублях"

                        text = f'✅ Введите нужную сумму в {addTxt}\n' \
                               '🤖Оплата будет проверена автоматически.'

                        await UserStates.Buy.set()
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb("Buy", "currency_buy"))

                    elif data.get('action') == "confirmation_buy":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        if user.transaction_timer:
                            await callback.message.edit_text(text="📎 Отправьте скрин перевода, либо чек оплаты!")
                            await UserStates.UserPhoto.set()
                        else:
                            await callback.message.delete()
                            await callback.message.answer(text="У вас вышло время на оплату!")
                            await callback.message.answer(text=f"{CONFIGTEXT.MAIN_FORM.TEXT}",
                                                          reply_markup=await MainForms.main_kb())
                            user.transaction_timer = False
                            await CRUDUsers.update(user=user)
                            await state.finish()

                elif data.get("target") == "Sell":
                    if data.get("action") == "currency_buy":
                        await state.finish()

                        await state.update_data(exchangeType="sell")
                        await state.update_data(currency="BYN")
                        await state.update_data(currency_abbreviation="BYN")

                        text = "Выберите валюту которую вы хотите продать."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.coin_ikb(target="Sell",
                                                                                               action="coin_buy")
                                                         )

                    elif data.get('action') == "coin_buy":
                        coin_id = data.get('id')

                        await state.update_data(exchangeType="sell")
                        await state.update_data(currency="BYN")
                        await state.update_data(currency_abbreviation="BYN")

                        await state.update_data(coin=coin_id)
                        text = f'✅ Введите нужную сумму в {coin_id}\n' \
                               '🤖Оплата будет проверена автоматически.'

                        await UserStates.Buy.set()
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb(target="Sell",
                                                                                               action="currency_buy"))

                    elif data.get('action') == "confirmation_buy":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        if user.transaction_timer:
                            await callback.message.edit_text(text="📎 Отправьте скрин перевода, либо чек оплаты!")
                            await UserStates.UserPhoto.set()
                        else:
                            await callback.message.delete()
                            await callback.message.answer(text=f"У вас вышло время на оплату!\n\n"
                                                               f"{CONFIGTEXT.MAIN_FORM.TEXT}",
                                                          reply_markup=await MainForms.main_kb())
                            user.transaction_timer = False
                            await CRUDUsers.update(user=user)
                            await state.finish()

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
                if await state.get_state() == "UserStates:Buy":
                    getData = await state.get_data()
                    if getData['exchangeType'] == "buy":
                        if message.text.isdigit():
                            if CONFIG.COMMISSION.MIN_BYN <= int(message.text):
                                try:
                                    amount = await Check_currency.commaToDot(amount=message.text)

                                    await state.update_data(amount=amount)
                                    get_state_data = await state.get_data()
                                    abbreviation = await MainForms.abbreviation(get_state_data['coin'])
                                    buy = await MainForms.buy(coin=get_state_data['coin'],
                                                              currency=get_state_data['currency'],
                                                              amount=get_state_data['amount'])

                                    await state.update_data(buy=buy)
                                    check_currency = Check_currency(amount=get_state_data['amount'],
                                                                    abbreviation=abbreviation,
                                                                    exchange_type=get_state_data['exchangeType'],
                                                                    buy=buy,
                                                                    currency=get_state_data['currency'],
                                                                    coin=get_state_data['coin'])

                                    get_text = await check_currency.get_text_Buy(integerNumber=True, state=state)

                                    if get_text:
                                        if get_state_data['exchangeType'] == "sell":
                                            await message.answer(text=get_text,
                                                                 reply_markup=await MainForms.back_ikb(
                                                                     target="Sell",
                                                                     action="currency_buy"),
                                                                 parse_mode="HTML")

                                            user = await CRUDUsers.get(user_id=message.from_user.id)
                                            user.transaction_timer = True
                                            await CRUDUsers.update(user=user)

                                        else:
                                            await message.answer(text=get_text[0])
                                            await message.answer(text=get_text[1],
                                                                 reply_markup=await MainForms.back_ikb(
                                                                     target="Buy",
                                                                     action="currency_buy"),
                                                                 parse_mode="HTML")
                                            user = await CRUDUsers.get(user_id=message.from_user.id)
                                            user.transaction_timer = True
                                            await CRUDUsers.update(user=user)
                                    else:
                                        await message.answer(text="Не вверно введены данные",
                                                             reply_markup=await MainForms.back_ikb(
                                                                 target="Buy",
                                                                 action="currency_buy"))
                                        await UserStates.Buy.set()
                                except ValueError as e:
                                    await message.answer(text="Не вверно введены данные",
                                                         reply_markup=await MainForms.back_ikb(
                                                             target="Buy",
                                                             action="currency_buy"))
                                    await UserStates.Buy.set()
                                    logging.error(f"Error {e}")
                            else:
                                await message.answer(text=f"Минимальная сумма {CONFIG.COMMISSION.MIN_BYN} BYN\n"
                                                          f"Введите новую сумму",
                                                     reply_markup=await MainForms.back_ikb(target="Buy",
                                                                                           action="currency_buy"))
                                await UserStates.Buy.set()
                        else:
                            await message.answer(text="Неверно введены данные!\n"
                                                      "Введите заново")
                            await UserStates.Buy.set()
                    else:
                        try:
                            amount = await Check_currency.commaToDot(amount=message.text)

                            await state.update_data(amount=amount)
                            get_state_data = await state.get_data()
                            abbreviation = await MainForms.abbreviation(get_state_data['coin'])
                            buy = await MainForms.buy(coin=get_state_data['coin'],
                                                      currency=get_state_data['currency'],
                                                      amount=get_state_data['amount'])

                            await state.update_data(buy=buy)

                            check_currency = Check_currency(amount=get_state_data['amount'],
                                                            abbreviation=abbreviation,
                                                            exchange_type=get_state_data['exchangeType'],
                                                            buy=buy,
                                                            currency=get_state_data['currency'],
                                                            coin=get_state_data['coin'])

                            if get_state_data['exchangeType'] == "sell":
                                get_text = await check_currency.get_text_Buy(state=state)
                            else:
                                get_text = await check_currency.get_text_Buy(integerNumber=True, state=state)

                            if get_text:
                                if get_state_data['exchangeType'] == "sell":
                                    await message.answer(text=get_text,
                                                         reply_markup=await MainForms.back_ikb(target="Main",
                                                                                               action="main"),
                                                         parse_mode="HTML")

                                    user = await CRUDUsers.get(user_id=message.from_user.id)
                                    user.transaction_timer = True
                                    await CRUDUsers.update(user=user)
                                else:
                                    await message.answer(text=get_text[0])
                                    await message.answer(text=get_text[1],
                                                         reply_markup=await MainForms.back_ikb(target="Main",
                                                                                               action="main"),
                                                         parse_mode="HTML")

                                    user = await CRUDUsers.get(user_id=message.from_user.id)
                                    user.transaction_timer = True
                                    await CRUDUsers.update(user=user)
                            else:
                                await message.answer(text="Не вверно введены данные",
                                                     reply_markup=await MainForms.back_ikb(target="Main",
                                                                                           action="main"))
                                await UserStates.Buy.set()
                        except ValueError as e:
                            await message.answer(text="Не вверно введены данные",
                                                 reply_markup=await MainForms.back_ikb(target="Main", action="main"))
                            await UserStates.Buy.set()
                            logging.error(f"Error {e}")
                    user = await CRUDUsers.get(user_id=message.from_user.id)
                    user.transaction_timer = True
                    await CRUDUsers.update(user=user)

                elif await state.get_state() == "UserStates:ERIP":
                    get_state_data = await state.get_data()
                    abbreviation = await MainForms.abbreviation(get_state_data['coin'])

                    text = "✅Заявка успешно создана.\n\n" \
                           f"Продаете: <code>{get_state_data['amount']} {get_state_data['coin']}</code>\n" \
                           f"ЕРИП РБ реквизиты: <code>{message.text}</code>\n\n" \
                           f"💵Получаете: <code>{round(get_state_data['buy'],2)} {get_state_data['currency_abbreviation']}</code>\n\n" \
                           f"<b>Реквизиты для перевода {get_state_data['coin']}</b>:\n\n" \
                           f"{CONFIGTEXT.Wallet.TEXT}\n\n"\
                           "⏳<b>Заявка действительна: <code>15 минут</code></b>\n\n" \
                           '☑️После успешного перевода денег по указанному кошельку нажмите на кнопку ' \
                           '"<b>Я оплатил(а)</b>" или же вы можете отменить данную заявку, ' \
                           'нажав на кнопку "<b>Отменить заявку</b>".'

                    await message.answer(text=text,
                                         reply_markup=await MainForms.confirmation_ikb(target="Sell",
                                                                                       action="confirmation_buy"),
                                         parse_mode="HTML")

                    await state.update_data(erip=message.text)
                    user = await CRUDUsers.get(user_id=message.from_user.id)
                    user.transaction_timer = True
                    await CRUDUsers.update(user=user)

                    await asyncio.sleep(int(60))
                    await MainForms.send_timer_message(chat_id=message.from_user.id, state=state)

                elif await state.get_state() == "UserStates:Wallet":
                    user = await CRUDUsers.get(user_id=message.from_user.id)
                    if user.transaction_timer:
                        data_state = await state.get_data()
                        if data_state['coin'] == "USDT":
                            wallet = await Cryptocurrency.Check_Wallet_USDT(address=message.text)
                        else:
                            wallet = await Cryptocurrency.Check_Wallet(btc_address=message.text)

                        get_state_data = await state.get_data()
                        if wallet:
                            await state.update_data(wallet=message.text)
                            if get_state_data['exchangeType'] == "buy":
                                text = await MainForms.receipt(state=state, message=message)

                            await message.answer(text=text,
                                                 reply_markup=await MainForms.confirmation_ikb(target="Buy",
                                                                                               action="confirmation_buy"),
                                                 parse_mode="HTML")

                            await asyncio.sleep(int(60))
                            await MainForms.send_timer_message(chat_id=message.from_user.id, state=state)

                        else:
                            text = f"Адреса кошелька <code>{message.text}</code> нет в blockchain\n" \
                                   f"Введите еще раз адрес"
                            await message.answer(text=text, parse_mode="HTML",
                                                 reply_markup=await MainForms.back_ikb(target="Main", action="main"))
                    else:
                        await message.answer(text=f"У вас вышло время на оплату!\n"
                                                  f"{CONFIGTEXT.MAIN_FORM.TEXT}",
                                             reply_markup=await MainForms.main_kb())
                        user.transaction_timer = False
                        await CRUDUsers.update(user=user)
                        await state.finish()

                elif await state.get_state() == "UserStates:UserPhoto":
                    user = await CRUDUsers.get(user_id=message.from_user.id)
                    if user.transaction_timer:
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
                                            currency="BYN",
                                            purchase_id=1,
                                            quantity=float(get_state_data['amount']),
                                            coin=get_state_data['coin'],
                                            price_per_unit=float(get_state_data['buy']),
                                            wallet=get_state_data['wallet']
                                        ))
                                        transaction = await CRUDTransactions.add(transaction=TransactionsSchema(
                                            purchase_id=purchase.id
                                        ))
                                        applicationNumber = await CRUDPurchases.get(id=purchase.id)
                                        applicationNumber.purchase_id = applicationNumber.id + 449112
                                        await CRUDPurchases.update(purchase=applicationNumber)

                                        applicationNumber_id = applicationNumber.id + 449112

                                    if get_state_data['exchangeType'] == "sell":
                                        sale = await CRUDSales.add(sale=SalesSchema(
                                            user_id=user.id,
                                            currency="BYN",
                                            sale_id=1,
                                            quantity=get_state_data['amount'],
                                            coin=get_state_data['coin'],
                                            price_per_unit=get_state_data['buy'],
                                            erip=get_state_data['erip']
                                        ))
                                        transaction = await CRUDTransactions.add(transaction=TransactionsSchema(
                                            sale_id=sale.id
                                        ))
                                        applicationNumber = await CRUDSales.get(id=sale.id)
                                        applicationNumber.sale_id = applicationNumber.id + 549112

                                        await CRUDSales.update(sale=applicationNumber)
                                        applicationNumber_id = applicationNumber.id + 549112

                                except Exception as e:
                                    logging.error(f'Error add что происодит я хз in db: {e}')

                                try:
                                    if transaction:
                                        get_applicationNumber = applicationNumber_id
                                        await bot.download_file(file_path=get_photo.file_path,
                                                                destination=f'user_check/{get_applicationNumber}'
                                                                            f'_{message.from_user.id}.jpg',
                                                                timeout=12,
                                                                chunk_size=1215000)

                                        await MainForms.messageAdministrators(message=message,
                                                                              state=state,
                                                                              photo=photo,
                                                                              applicationNumber=get_applicationNumber)
                                        user.transaction_timer = False
                                        await CRUDUsers.update(user=user)
                                        await state.finish()
                                    else:
                                        await message.answer(text="Ошибка, попробуйте снова или "
                                                                  "обратитесь к администраторам",
                                                             reply_markup=await MainForms.back_ikb(target="Main",
                                                                                                   action="main"))
                                except Exception as e:
                                    logging.error(f'Error UserStates:UserPhoto: {e}')
                        else:
                            await message.answer(text="Нужно фото!")
                            await UserStates.UserPhoto.set()
                    else:
                        await message.answer(text="У вас вышло время!, на оплату\n\n"
                                                  f"{CONFIGTEXT.MAIN_FORM.TEXT}",
                                             reply_markup=await MainForms.main_kb())
                        user.transaction_timer = False
                        await CRUDUsers.update(user=user)
                        await state.finish()
