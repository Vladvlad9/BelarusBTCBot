import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from states.users.userStates import UserStates

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForms:
    @staticmethod
    async def abbreviation(coin: str):
        data = {
            "Bitcoin": "btc",
            "Litecoin": "ltc",
            "USDT(trc20)": "usdt",
            "Monero(XMR)": "xmr",
            "RUB": "₽",
            "BUN": "Br",
        }
        if coin in data:
            return data[coin]

    @staticmethod
    async def bue(coin: str, currency: str, amount: str):
        if coin == "RUB":
            price_BTC: float = await Cryptocurrency.get_btc()
            buy: float = round(float(amount) * price_BTC, 8)
            return buy

        elif coin == "BYN":
            price_BTC: float = await Cryptocurrency.get_btc()
            buy: float = round(float(amount) * price_BTC, 8)

            return buy

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
                                         callback_data=main_cb.new(target, action, "BUN", 0)),
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
            "❌Litecoin": {"target": target, "action": action, "id": "Litecoin", "editId": 0},
            "❌USDT(trc20)": {"target": target, "action": action, "id": "USDT(trc20)", "editId": 0},
            "❌Monero(XMR)": {"target": target, "action": action, "id": "Monero(XMR)", "editId": 0},
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
                ]for name, name_items in data.items()
            ] + [
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("Buy", "getBuy", 0, 0))
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
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("main"):
                data = main_cb.parse(callback_data=callback.data)

                if data.get("target") == "Main":
                    await state.finish()
                    text = "Приветствие!"
                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForms.main_ikb())

                elif data.get("target") == "Buy":
                    if data.get("action") == "getBuy":
                        text = "Выберите валюту."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.currency_ikb(
                                                             target='Buy',
                                                             action='currency_buy')
                                                         )

                    elif data.get("action") == "currency_buy":
                        await state.update_data(currency=data.get("id"))
                        await state.update_data(currency_abbreviation=await MainForms.abbreviation(data.get("id")))
                        text = "Выберите валюту которую вы хотите продать."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.coin_ikb(target="Buy",
                                                                                               action="coin_buy")
                                                         )

                    elif data.get('action') == "coin_buy":
                        coin_id = data.get('id')
                        await state.update_data(coin=coin_id)
                        text = f'✅ Введите нужную сумму в {coin_id}\n' \
                               '🤖Оплата будет проверена автоматически.'

                        await UserStates.Buy.set()
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb("Buy", "currency_buy"))

                    elif data.get('action') == "confirmation_buy":
                        await callback.message.edit_text(text="📸 Загрузите изображение подтверждающее оплату!\n"
                                                              "(до 2 Мб)")
                        #await UserStates.UserPhoto.set()

                elif data.get("target") == "Sell":
                    if data.get("action") == "getSell":
                        text = "Продать"
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.main_ikb())

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
                    await state.update_data(amount=message.text)
                    get_state_data = await state.get_data()
                    abbreviation = await MainForms.abbreviation(get_state_data['coin'])

                    price_BTC: float = await Cryptocurrency.get_btc()
                    buy: float = round(float(message.text) * price_BTC, 8)
                    await state.update_data(buy=buy)
                    text = f"Сумма к получению: {message.text} {get_state_data['coin']}\n" \
                           f"Сумма к оплате: {buy} {get_state_data['currency_abbreviation']}\n\n" \
                           f"📝Введите {get_state_data['coin']}-адрес кошелька, " \
                           f"куда вы хотите отправить {message.text} {abbreviation}"
                    await message.answer(text=text,
                                         reply_markup=await MainForms.back_ikb(target="Main", action="0"))
                    await UserStates.Wallet.set()

                elif await state.get_state() == "UserStates:Wallet":
                    await state.update_data(wallet=message.text)
                    get_state_data = await state.get_data()
                    text = f"✅Заявка №1 успешно создана.\n\n" \
                           f"Получаете: {get_state_data['amount']} {get_state_data['coin']}\n" \
                           f"{get_state_data['coin']}-адрес: <code>{message.text}</code>\n\n" \
                           f"Ваш ранг: 👶, скидка 0.0%\n\n" \
                           f"💵Сумма к оплате: {get_state_data['buy']} {get_state_data['currency_abbreviation']}\n" \
                           f"Резквизиты для оплаты:\n\n" \
                           f"🟢 2202206403717908\n\n" \
                           f"СБП +79190480534 (Сбербанк)\n\n" \
                           f"⏳Заявка действительна: 15 минут\n\n" \
                           f'☑️После успешного перевода денег по указанным реквизитам нажмите на кнопку ' \
                           f'"Я оплатил(а)" или же вы можете отменить данную заявку, нажав на кнопку "Отменить заявку".'
                    await message.answer(text=text,
                                         reply_markup=await MainForms.confirmation_ikb(target="Buy",
                                                                                       action="confirmation_buy"),
                                         parse_mode="HTML")
                    #await state.finish()
