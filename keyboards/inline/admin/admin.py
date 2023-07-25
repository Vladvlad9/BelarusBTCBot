from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, InputFile
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
# from crud import CRUDUsers, CRUDTransaction, CRUDCurrency, CRUDOperation
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
    async def Text_change_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели
        :return:
        """
        data = {"При первом входе": {"target": "Text_change", "action": "FIRST_PAGE", "id": 0, "editid": 0},
                "Главное меню": {"target": "Text_change", "action": "MAIN_FORM", "id": 0, "editid": 0},
                "Реквизиты BYN": {"target": "Text_change", "action": "RequisitesBYN", "id": 0, "editid": 0},
                "Реквизиты RUS": {"target": "Text_change", "action": "RequisitesRUS", "id": 0, "editid": 0},
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
        data = {"% Комиссия": {"target": "PaymentSetup", "action": "get_Commission", "id": 0, "editId": 0},
                "🧾 Расчетный Счет": {"target": "PaymentSetup", "action": "get_Settlement_Account", "id": 0,
                                      "editId": 0},
                "⏱ Таймер оплаты": {"target": "PaymentSetup", "action": "get_Timer", "id": 0, "editId": 0},
                "🇧🇾 Минимально BYN": {"target": "PaymentSetup", "action": "get_MinBYN", "id": 0, "editId": 0},
                "🇷🇺 Минимально RUB": {"target": "PaymentSetup", "action": "get_MinRUB", "id": 0, "editId": 0},
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