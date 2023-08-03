import asyncio
import re

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, InputFile
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from config.config import CONFIGTEXT
from crud import CRUDUsers
from crud.purchaseCRUD import CRUDPurchases
from crud.saleCRUD import CRUDSales
from handlers.AllCallbacks import admin_cb
from loader import bot
from states.admins.AdminState import AdminState

import pandas as pd


class AdminForm:

    @staticmethod
    async def back_ikb(target: str, action: str = None) -> InlineKeyboardMarkup:
        """
        Общая клавиатура для перехода на один шаг назад
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=admin_cb.new(target, action, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def change_ikb(get_change: str) -> InlineKeyboardMarkup:
        """
        Клавиатура для изменения данных Комиссии(0) или Расчётный счёт(1)
        :param get_change: необходим для того что бы отслеживать что выбрал админ 1 или 0
        :return:
        """
        data = {"🔁 Изменить": {"target": "PaymentSetup", "action": "get_change", "id": 1, "editId": get_change},
                "◀️ Назад": {"target": "PaymentSetup", "action": "get_Setup", "id": 2, "editId": get_change},
                }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editId"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def start_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели
        :return:
        """
        data = {"⚙️ Настройка Оплаты": {"target": "PaymentSetup", "action": "get_Setup", "id": 0, "editid": 0},
                "📨 Рассылка": {"target": "Newsletter", "action": "get_Newsletter", "id": 0, "editid": 0},
                "📝 Изменение текста": {"target": "Text_change", "action": "get_Сhange", "id": 0, "editid": 0},
                "👨‍💻 Пользователи": {"target": "Users", "action": "get_Users", "id": 0, "editid": 0},
                "Продажа": {"target": "Sale", "action": "get_Sale", "id": 0, "editid": 0},
                "Покупка": {"target": "Buy", "action": "get_Buy", "id": 0, "editid": 0},
                "📊 Отчет": {"target": "Report", "action": "get_Report", "id": 0, "editid": 0},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def report_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Продажи", callback_data=admin_cb.new("Report", "ReportSale", 0, 0))
                ],
                [
                    InlineKeyboardButton(text="Покупки", callback_data=admin_cb.new("Report", "ReportBuy", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def Text_change_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели
        :return:

        "Реквизиты BYN": {"target": "Text_change", "action": "RequisitesBYN", "id": 0, "editid": 0},
                "Реквизиты RUS": {"target": "Text_change", "action": "RequisitesRUS", "id": 0, "editid": 0},
        """
        data = {"При первом входе": {"target": "Text_change", "action": "FIRST_PAGE", "id": 0, "editid": 0},
                "Главное меню": {"target": "Text_change", "action": "MAIN_FORM", "id": 0, "editid": 0},
                "◀️ Назад": {"target": "StartMenu", "action": "", "id": 0, "editid": 0},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def newsletter_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели
        :return:
        """
        data = {"🏞 Картинка": {"target": "Newsletter", "action": "get_Picture", "id": 0, "editid": 0},
                "🗒 Текст": {"target": "Newsletter", "action": "get_Text", "id": 0, "editid": 0},
                "🏞 Картинка + Текст 🗒": {"target": "Newsletter", "action": "get_PicTex", "id": 1, "editid": 0},
                "◀️ Назад": {"target": "StartMenu", "action": "", "id": 0, "editid": 0},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def payment_setup_ikb() -> InlineKeyboardMarkup:
        data = {
            "% Комиссия Покупки": {"target": "PaymentSetup", "action": "get_CommissionBuy", "id": 0, "editId": 0},
            "% Комиссия Продажи": {"target": "PaymentSetup", "action": "get_CommissionSale", "id": 0, "editId": 0},
            "🧾 ЕРИП": {"target": "PaymentSetup", "action": "get_Settlement_Account", "id": 0, "editId": 0},
            "👛 Кошелек": {"target": "PaymentSetup", "action": "get_Wallet", "id": 0, "editId": 0},
            "⏱ Таймер оплаты": {"target": "PaymentSetup", "action": "get_Timer", "id": 0, "editId": 0},
            "🇧🇾 Минимально BYN": {"target": "PaymentSetup", "action": "get_MinBYN", "id": 0, "editId": 0},
            "◀️ Назад": {"target": "StartMenu", "action": "", "id": 0, "editId": 0},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editId"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def process_admin_profile(callback: CallbackQuery = None, message: Message = None,
                                    state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith('admin'):
                data = admin_cb.parse(callback_data=callback.data)

                if data.get("target") == "StartMenu":
                    await callback.message.edit_text(text="Админ панель",
                                                     reply_markup=await AdminForm.start_ikb())

                elif data.get("target") == "PaymentSetup":
                    if data.get("action") == "get_Setup":
                        await callback.message.edit_text(text="Настройка оплаты",
                                                         reply_markup=await AdminForm.payment_setup_ikb())
                        await state.finish()

                    elif data.get("action") == "get_CommissionSale":
                        await callback.message.edit_text(text=f"Комиссия Продажи составляет "
                                                              f"{CONFIG.COMMISSION.COMMISSION_SALES}%",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="CommissionSale")
                                                         )

                    elif data.get("action") == "get_CommissionBuy":
                        await callback.message.edit_text(text=f"Комиссия покупки составляет "
                                                              f"{CONFIG.COMMISSION.COMMISSION_BUY}%",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="CommissionBuy")
                                                         )

                    elif data.get("action") == "get_Settlement_Account":
                        await callback.message.edit_text(text=f"<b>Реквизиты для оплаты:</b>\n\n"
                                                              f"{CONFIGTEXT.RequisitesBYN.TEXT}",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="REQUISITES"),
                                                         parse_mode="HTML"
                                                         )
                        await AdminState.REQUISITES.set()

                    elif data.get("action") == "get_change":
                        get_change_data = str(data.get("editId"))
                        text, target, action = "", "", ""

                        if get_change_data == "CommissionSale":
                            text = "Введите данные Комиссии для продажи в формате '1.__'"
                            target = "PaymentSetup"
                            action = "get_Setup"
                            await AdminState.COMMISSIONSale.set()

                        if get_change_data == "CommissionBuy":
                            text = "Введите данные Покупки для продажи в формате '1.__'"
                            target = "PaymentSetup"
                            action = "get_Setup"
                            await AdminState.COMMISSIONBuy.set()

                        elif get_change_data == "REQUISITES":
                            text = "Введите новые данные для Расчётного счёта"
                            target = "PaymentSetup"
                            action = "get_Setup"
                            await AdminState.REQUISITES.set()

                        elif get_change_data == "TIMER":
                            text = "Введите новые данные для Таймера в <b>минутах</b>"
                            target = "PaymentSetup"
                            action = "get_Setup"
                            await AdminState.Timer.set()

                        elif get_change_data == "MinBYN":
                            text = "Введите новую минимальную сумму для BYN"
                            target = "PaymentSetup"
                            action = "get_Setup"
                            await AdminState.MinBYN.set()

                        elif get_change_data == "FIRST_PAGE":
                            text = "Введите текст для ввода Captcha"
                            target = "Text_change"
                            action = "get_Сhange"
                            await AdminState.FIRST_PAGE.set()

                        elif get_change_data == "MAIN_FORM":
                            text = "Введите текст для Главного меню"
                            target = "Text_change"
                            action = "get_Сhange"
                            await AdminState.MAIN_FORM.set()

                        elif get_change_data == "RequisitesBYN":
                            text = "Введите данные для реквизитов"
                            target = "Text_change"
                            action = "get_Сhange"
                            await AdminState.RequisitesBYN.set()

                        elif get_change_data == "Wallet":
                            text = "Введите Реквизиты для перевода Bitcoin:"
                            target = "PaymentSetup"
                            action = "get_Setup"
                            await AdminState.WALLET.set()

                        await callback.message.edit_text(text=text,
                                                         parse_mode="HTML",
                                                         reply_markup=await AdminForm.back_ikb(target=target,
                                                                                               action=action)
                                                         )

                    elif data.get("action") == "get_Timer":
                        await callback.message.edit_text(text=f"Таймер: {CONFIG.PAYMENT_TIMER/60} мин.",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="TIMER")
                                                         )
                        await AdminState.Timer.set()

                    elif data.get("action") == "get_MinBYN":
                        await callback.message.edit_text(text=f"Минимальная сумма BYN: {CONFIG.COMMISSION.MIN_BYN} руб.",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="MinBYN")
                                                         )
                        await AdminState.MinBYN.set()

                    elif data.get("action") == "get_Wallet":
                        await callback.message.edit_text(text=f"Реквизиты для перевода Bitcoin: \n"
                                                              f"{CONFIGTEXT.Wallet.TEXT} ",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="Wallet")
                                                         )
                        await AdminState.WALLET.set()

                elif data.get("target") == "Newsletter":
                    await state.finish()

                    if data.get("action") == "get_Newsletter":
                        text = "Вы можете выделять текст жирным шрифтом или курсивом, добавлять стиль кода или " \
                               "гиперссылки для лучшей визуализации важной информации.\n\n" \
                               "Список поддерживаемых тегов:\n" \
                               "b<b> текст </b>/b - Выделяет текст жирным шрифтом\n" \
                               "i<i> текст </i>/i - Выделяет текст курсивом\n" \
                               "u<u> текст </u>/u - Выделяет текст подчеркиванием\n" \
                               "s<s> текст </s>/s - Добавляет зачеркивание текста\n" \
                               "tg-spoiler<tg-spoiler> текст </tg-spoiler>/tg-spoiler - Добавляет защиту от спойлера, " \
                               "которая скрывает выделенный текст\n" \
                               "<a href='http://www.tg.com/'>текст</a> - Создает гиперссылку на выделенный текст"
                        await callback.message.edit_text(text=f"{text}",
                                                         reply_markup=await AdminForm.newsletter_ikb())
                        # await AdminState.Newsletter.set()

                    elif data.get('action') == "get_Picture":
                        id = data.get('id')
                        await state.update_data(id=id)
                        await callback.message.edit_text(text="Выберите картинку!",
                                                         reply_markup=await AdminForm.back_ikb(
                                                             target="Newsletter",
                                                             action="get_Newsletter")
                                                         )
                        await AdminState.NewsletterPhoto.set()

                    elif data.get('action') == "get_Text":
                        id = data.get('id')
                        await state.update_data(id=id)
                        await callback.message.edit_text(text="Введите текст, так же можете его отформатировать",
                                                         reply_markup=await AdminForm.back_ikb(
                                                             target="Newsletter",
                                                             action="get_Newsletter")
                                                         )
                        await AdminState.NewsletterText.set()

                    elif data.get('action') == "get_PicTex":
                        id = data.get('id')
                        await state.update_data(id=id)
                        await callback.message.edit_text(text="Введите текст!",
                                                         reply_markup=await AdminForm.back_ikb(
                                                             target="Newsletter",
                                                             action="get_Newsletter")
                                                         )
                        await AdminState.NewsletterText.set()

                elif data.get('target') == "Report":
                    if data.get('action') == "get_Report":
                        await callback.message.edit_text(text="Выберите",
                                                         reply_markup=await AdminForm.report_ikb())

                    elif data.get('action') == "ReportSale":
                        sales = await CRUDSales.get_all()
                        user_id = []
                        sale_id = []
                        currency = []
                        coin = []
                        erip = []
                        quantity = []
                        price_per_unit = []
                        commission = []
                        date = []
                        status = []
                        moneyDifference = []

                        for sale in sales:
                            user = await CRUDUsers.get(id=sale.user_id)
                            get_status = "Не обработана" if sale.status else "Обработана"

                            user_id.append(user.user_id)
                            sale_id.append(sale.sale_id)
                            price_per_unit.append(sale.price_per_unit)
                            currency.append(sale.currency)

                            quantity.append(sale.quantity)
                            coin.append(sale.coin)
                            erip.append(sale.erip)
                            commission.append(sale.commission)
                            date.append(sale.date)
                            status.append(get_status)
                            moneyDifference.append(sale.moneyDifference)

                        df = pd.DataFrame({
                            'user_id': user_id,
                            'id Продажи': sale_id,
                            'Получено': price_per_unit,
                            'Валюта': currency,
                            'Продано': quantity,
                            'Монета': coin,
                            'Комиссия': commission,
                            'Разница': moneyDifference,
                            'ЕРИП': erip,
                            'Дата сделки': date,
                            'Статус': status
                        })
                        df.to_excel('Sale.xlsx')

                        await callback.message.answer_document(document=open('Sale.xlsx', 'rb'),
                                                               caption="Отчет сформирован",
                                                               parse_mode="HTML"
                                                               )

                    elif data.get('action') == "ReportBuy":
                        sales = await CRUDPurchases.get_all()
                        user_id = []
                        purchase_id = []
                        currency = []
                        coin = []
                        wallet = []
                        quantity = []
                        price_per_unit = []
                        date = []
                        commission = []
                        status = []
                        moneyDifference = []

                        for sale in sales:
                            user = await CRUDUsers.get(id=sale.user_id)
                            get_status = "Не обработана" if sale.status else "Обработана"

                            user_id.append(user.user_id)
                            purchase_id.append(sale.purchase_id)
                            price_per_unit.append(sale.price_per_unit)
                            currency.append(sale.currency)

                            quantity.append(sale.quantity)
                            coin.append(sale.coin)
                            wallet.append(sale.wallet)
                            commission.append(sale.commission)
                            date.append(sale.date)
                            status.append(get_status)
                            moneyDifference.append(sale.moneyDifference)

                        df = pd.DataFrame({
                            'id Пользователя': user_id,
                            'id Покупки': purchase_id,
                            'Получено': price_per_unit,
                            'Валюта': currency,
                            'Продано': quantity,
                            'Монета': coin,
                            'Разница': moneyDifference,
                            'Комиссия': commission,
                            'Кошелек': wallet,
                            'Дата сделки': date,
                            'Статус': status
                        })
                        df.to_excel('Buy.xlsx')

                        await callback.message.answer_document(document=open('Buy.xlsx', 'rb'),
                                                               caption="Отчет сформирован",
                                                               parse_mode="HTML"
                                                               )

                elif data.get('target') == "Text_change":
                    if data.get('action') == "get_Сhange":
                        await callback.message.edit_text(text="📝 Изменение текста",
                                                         reply_markup=await AdminForm.Text_change_ikb())

                    elif data.get("action") == "FIRST_PAGE":
                        await callback.message.edit_text(text=CONFIGTEXT.FIRST_PAGE.TEXT,
                                                         parse_mode="HTML",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="FIRST_PAGE")
                                                         )

                    elif data.get("action") == "MAIN_FORM":
                        await callback.message.edit_text(text=CONFIGTEXT.MAIN_FORM.TEXT,
                                                         parse_mode="HTML",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="MAIN_FORM")
                                                         )

                    elif data.get("action") == "RequisitesBYN":
                        await callback.message.edit_text(text=CONFIGTEXT.RequisitesBYN.TEXT,
                                                         parse_mode="HTML",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="RequisitesBYN")
                                                         )

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
                if await state.get_state() == "AdminState:REQUISITES":
                    CONFIGTEXT.RequisitesBYN.TEXT = f"{message.text}"
                    await message.answer(text="Вы успешно изменили текст",
                                         reply_markup=await AdminForm.start_ikb())
                    await state.finish()

                elif await state.get_state() == "AdminState:COMMISSIONSale":
                    if re.match(r'^1\.[0-9]{2}$', message.text):
                        CONFIG.COMMISSION.COMMISSION_SALES = message.text
                        await message.answer(text=f"Вы успешно изменили Комиссию Продажи "
                                                  f"на <code>{message.text}</code> %",
                                             parse_mode="HTML",
                                             reply_markup=await AdminForm.start_ikb())
                        await state.finish()
                    else:
                        await message.answer(text="Неверно введены данные (1.__)")
                        await AdminState.COMMISSIONSale

                elif await state.get_state() == "AdminState:COMMISSIONBuy":
                    if re.match(r'^1\.[0-9]{2}$', message.text):
                        CONFIG.COMMISSION.COMMISSION_BUY = message.text
                        await message.answer(text=f"Вы успешно изменили Комиссию Покупки на "
                                                  f"<code>{message.text}</code> %",
                                             parse_mode="HTML",
                                             reply_markup=await AdminForm.start_ikb())
                        await state.finish()
                    else:
                        await message.answer(text="Введите число!")
                        await AdminState.COMMISSIONBuy

                elif await state.get_state() == "AdminState:MinBYN":
                    if message.text.isdigit():
                        CONFIG.COMMISSION.MIN_BYN = int(message.text)
                        await message.answer(text=f"Вы успешно изменили Минимальную сумму "
                                                  f"<code>{int(message.text)} BYN</code>!",
                                             parse_mode='HTML',
                                             reply_markup=await AdminForm.start_ikb())
                        await state.finish()
                    else:
                        await message.answer(text='Введите число!')
                        await AdminState.MinBYN.set()

                elif await state.get_state() == "AdminState:Timer":
                    if message.text.isdigit():
                        CONFIG.PAYMENT_TIMER = int(message.text) * 60
                        await message.answer(text=f"Вы успешно изменили Таймер "
                                                  f"на <code>{int(message.text)}</code> минут(ы)",
                                             reply_markup=await AdminForm.start_ikb(),
                                             parse_mode="HTML")
                        await state.finish()
                    else:
                        await message.answer(text="Введите число!")
                        await AdminState.Timer.set()

                elif await state.get_state() == "AdminState:FIRST_PAGE":
                    CONFIGTEXT.FIRST_PAGE.TEXT = message.text
                    await message.answer(text="Вы успешно изменили текст",
                                         reply_markup=await AdminForm.start_ikb())
                    await state.finish()

                elif await state.get_state() == "AdminState:MAIN_FORM":
                    CONFIGTEXT.MAIN_FORM.TEXT = message.text
                    await message.answer(text="Вы успешно изменили текст",
                                         reply_markup=await AdminForm.start_ikb())
                    await state.finish()

                elif await state.get_state() == "AdminState:WALLET":
                    CONFIGTEXT.Wallet.TEXT = message.text
                    await message.answer(text=f"Вы успешно изменили реквизиты для перевода Bitcoin\n"
                                              f"<code>{message.text}</code>\n\n",
                                         parse_mode="HTML",
                                         reply_markup=await AdminForm.start_ikb())
                    await state.finish()

                elif await state.get_state() == "AdminState:NewsletterText":
                    try:
                        get_state = await state.get_data()
                        if int(get_state['id']) == 1:
                            await message.answer(text="Выберите картинку")
                            await state.update_data(caption=message.text)
                            await AdminState.NewsletterPhoto.set()
                        else:
                            users = await CRUDUsers.get_all()

                            tasks = []
                            for user in users:
                                tasks.append(bot.send_message(chat_id=user.user_id,
                                                              text=message.text,
                                                              parse_mode="HTML"))
                            await asyncio.gather(*tasks, return_exceptions=True)

                            await state.finish()
                    except Exception as e:
                        print(e)

                elif await state.get_state() == "AdminState:NewsletterPhoto":
                    if message.content_type == "photo":
                        try:
                            state_id = await state.get_data()
                            users = await CRUDUsers.get_all()
                            if int(state_id['id']) == 1:
                                tasks = []
                                for user in users:
                                    tasks.append(bot.send_photo(chat_id=user.user_id, photo=message.photo[2].file_id,
                                                                caption=state_id['caption']))
                                await asyncio.gather(*tasks, return_exceptions=True)
                            else:
                                tasks = []
                                for user in users:
                                    tasks.append(bot.send_photo(chat_id=user.user_id, photo=message.photo[2].file_id))
                                await asyncio.gather(*tasks, return_exceptions=True)

                        except Exception as e:
                            print(e)

                        await state.finish()
                        await message.answer(text="Рассылка картинки прошла успешно",
                                             reply_markup=await AdminForm.start_ikb()
                                             )
                    else:
                        await message.answer(text="Это не картинка!\n"
                                                  "Попробуйте еще раз",
                                             reply_markup=await AdminForm.back_ikb(
                                                 target="Newsletter",
                                                 action="get_Newsletter")
                                             )
                        await AdminState.NewsletterPhoto.set()
