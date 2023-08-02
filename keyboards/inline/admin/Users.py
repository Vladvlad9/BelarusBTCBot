import random

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, MediaGroup, InputFile
from aiogram.utils.exceptions import BadRequest

from crud import CRUDUsers
from crud.purchaseCRUD import CRUDPurchases
from crud.saleCRUD import CRUDSales
from handlers.AllCallbacks import admin_cb, user_cb
from keyboards.inline.admin.admin import AdminForm
from loader import bot
from states.admins.AdminState import AdminState


class Users:

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
    async def sell_or_buy_ikb(user_id: int) -> InlineKeyboardMarkup:
        """
        Клавиатура для того что бы потвердить пользовательское соглашение когда заходит в самый первый раз
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Покупка",
                                         callback_data=user_cb.new("UsersId", "Buying", 0, user_id, 0))
                ],
                [
                    InlineKeyboardButton(text="Продажа",
                                         callback_data=user_cb.new("UsersId", "Sale", 0, user_id, 0))
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад",
                                         callback_data=user_cb.new("Profile", "get_Profile", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def check_confirmation_ikb(target: str,
                                     user_id: int,
                                     sale_id: int,
                                     page: int = 0,
                                     getSale=False,
                                     action_back: str = None,
                                     action_confirm: str = None) -> InlineKeyboardMarkup:
        """
        Клавиатура для взаимодействия с транзакцией пользователя
        :param user_id: id Пользователя
        :param page: не обходимо для того что бы возвращаться к определенной странице
        :param action_back: не обходимо для того что бы возвращаться на определеную страницу
        :param action_confirm: не обходимо для того что бы возвращаться на определеную страницу
        :return:
        """

        user = await CRUDUsers.get(id=user_id)
        chat = await bot.get_chat(chat_id=user.user_id)
        button_url = chat.user_url

        data = {
            "✅ Потвердить Оплату": {
                "target": target,
                "action": action_confirm,
                "pagination": getSale,
                "id": sale_id,
                "editid": user_id
            },

            "◀️ Назад": {
                "target": target, "action": action_back, "pagination": "", "id": page, "editid": user_id},
        }
        if getSale:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📲 Связаться", url=button_url),
                        InlineKeyboardButton(text="◀️ Назад", callback_data=user_cb.new(target, action_back, 0, page, user_id))
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(text="📲 Связаться", url=button_url)
                                    ]

                                ] + [
                                    [
                                        InlineKeyboardButton(text=name, callback_data=user_cb.new(name_items["target"],
                                                                                                  name_items["action"],
                                                                                                  name_items[
                                                                                                      "pagination"],
                                                                                                  name_items["id"],
                                                                                                  name_items["editid"])
                                                             )
                                    ] for name, name_items in data.items()
                                ]
            )

    @staticmethod
    async def users_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели

        :return:
        """
        data = {
            # "#️⃣ Номер чека": {
            #     "target": "UsersCheck",
            #     "action": "get_CheckNumber",
            #     "pagination": "",
            #     "id": 0,
            #     "editid": 0
            # },

            "🆔 id Пользователя": {
                "target": "UsersId",
                "action": "get_UsersId",
                "pagination": "",
                "id": 0,
                "editid": 0
            },
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=name, callback_data=user_cb.new(name_items["target"],
                                                                                              name_items["action"],
                                                                                              name_items["pagination"],
                                                                                              name_items["id"],
                                                                                              name_items["editid"]))
                                ] for name, name_items in data.items()

                            ] + [
                                [
                                    InlineKeyboardButton(text="◀️ Назад",
                                                         callback_data=user_cb.new("MainMenu", "", 0, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def pagination_bue_ikb(target: str,
                                 user_id: int = None,
                                 action: str = None,
                                 page: int = 0) -> InlineKeyboardMarkup:
        """
        Клавиатура пагинации проведенных операций пользователя
        :param action_back:
        :param target:  Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param page: текущая страница пагинации
        :return:
        """
        if user_id:
            orders = await CRUDPurchases.get_all(user_id=user_id)
        # else:
        #     orders = await CRUDTransaction.get_all()

        orders_count = len(orders)

        prev_page: int
        next_page: int

        if page == 0:
            prev_page = orders_count - 1
            next_page = page + 1
        elif page == orders_count - 1:
            prev_page = page - 1
            next_page = 0
        else:
            prev_page = page - 1
            next_page = page + 1

        back_ikb = InlineKeyboardButton("◀️ Назад", callback_data=user_cb.new("User", "get_User", 0, 0, user_id))
        prev_page_ikb = InlineKeyboardButton("←", callback_data=user_cb.new(target, action, 0, prev_page, user_id))
        check = InlineKeyboardButton("☰", callback_data=user_cb.new("UsersId",
                                                                    "get_check_buy", 0, page, user_id))
        page = InlineKeyboardButton(f"{str(page + 1)}/{str(orders_count)}",
                                    callback_data=user_cb.new("", "", 0, 0, 0))
        next_page_ikb = InlineKeyboardButton("→", callback_data=user_cb.new(target, action, 0, next_page, user_id))

        if orders_count == 1:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        check
                    ],
                    [
                        back_ikb
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        prev_page_ikb,
                        page, check,
                        next_page_ikb,
                    ],
                    [
                        back_ikb
                    ]
                ]
            )

    @staticmethod
    async def buy_ikb() -> InlineKeyboardMarkup:
        buyTrue = list(filter(lambda x: x.status, await CRUDPurchases.get_all()))
        buyFalse = list(filter(lambda x: x.status == False, await CRUDPurchases.get_all()))

        data = {
            f"✅ Одобренные ({len(buyTrue)})": {
                "target": "Buy",
                "action": "BuyTrue",
                "pagination": "",
                "id": "Yes",
                "editid": 0
            },

            f"❌ Неодобренные ({len(buyFalse)})": {
                "target": "Buy",
                "action": "BuyFalse",
                "pagination": "",
                "id": "No",
                "editid": 0
            },
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=name, callback_data=user_cb.new(name_items["target"],
                                                                                              name_items["action"],
                                                                                              name_items["pagination"],
                                                                                              name_items["id"],
                                                                                              name_items["editid"]))
                                ] for name, name_items in data.items()

                            ] + [
                                [
                                    InlineKeyboardButton(text="◀️ Назад",
                                                         callback_data=user_cb.new("MainMenu", "", 0, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def sales_ikb() -> InlineKeyboardMarkup:
        salesTrue = list(filter(lambda x: x.status, await CRUDSales.get_all()))
        salesFalse = list(filter(lambda x: x.status == False, await CRUDSales.get_all()))

        data = {
            f"✅ Одобренные ({len(salesTrue)})": {
                "target": "Sale",
                "action": "SaleTrue",
                "pagination": "",
                "id": "Yes",
                "editid": 0
            },

            f"❌ Неодобренные ({len(salesFalse)})": {
                "target": "Sale",
                "action": "SaleFalse",
                "pagination": "",
                "id": "No",
                "editid": 0
            },
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=name, callback_data=user_cb.new(name_items["target"],
                                                                                              name_items["action"],
                                                                                              name_items["pagination"],
                                                                                              name_items["id"],
                                                                                              name_items["editid"]))
                                ] for name, name_items in data.items()

                            ] + [
                                [
                                    InlineKeyboardButton(text="◀️ Назад",
                                                         callback_data=user_cb.new("MainMenu", "", 0, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def pagination_sales_ikb(target: str,
                                   user_id: int = None,
                                   action: str = None,
                                   getSale: bool = False,
                                   page: int = 0) -> InlineKeyboardMarkup:
        """
        Клавиатура пагинации проведенных операций пользователя
        :param getSale:
        :param action_back:
        :param target:  Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param page: текущая страница пагинации
        :return:
        """
        if getSale:
            orders = list(filter(lambda x: x.status, await CRUDSales.get_all()))
            approved = True
        else:
            approved = False
            orders = list(filter(lambda x: x.status == False, await CRUDSales.get_all()))

        orders_count = len(orders)

        prev_page: int
        next_page: int

        if page == 0:
            prev_page = orders_count - 1
            next_page = page + 1
        elif page == orders_count - 1:
            prev_page = page - 1
            next_page = 0
        else:
            prev_page = page - 1
            next_page = page + 1

        back_ikb = InlineKeyboardButton("◀️ Назад", callback_data=admin_cb.new("Sale", "get_Sale", 0, user_id))
        prev_page_ikb = InlineKeyboardButton("←", callback_data=user_cb.new(target, action, 0, prev_page, user_id))
        check = InlineKeyboardButton("☰", callback_data=user_cb.new("Sale",
                                                                    "saleCheckApproved", bool(approved), page, user_id))
        page = InlineKeyboardButton(f"{str(page + 1)}/{str(orders_count)}",
                                    callback_data=user_cb.new("", "", 0, 0, 0))
        next_page_ikb = InlineKeyboardButton("→", callback_data=user_cb.new(target, action, 0, next_page, user_id))

        if orders_count == 1:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        check
                    ],
                    [
                        back_ikb
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        prev_page_ikb,
                        page, check,
                        next_page_ikb,
                    ],
                    [
                        back_ikb
                    ]
                ]
            )

    @staticmethod
    async def pagination_buy_ikb(target: str,
                                   user_id: int = None,
                                   action: str = None,
                                   getBuy: bool = False,
                                   page: int = 0) -> InlineKeyboardMarkup:
        """
        Клавиатура пагинации проведенных операций пользователя
        :param getBuy:
        :param action_back:
        :param target:  Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param page: текущая страница пагинации
        :return:
        """
        if getBuy:
            orders = list(filter(lambda x: x.status, await CRUDPurchases.get_all()))
            approved = True
        else:
            approved = False
            orders = list(filter(lambda x: x.status == False, await CRUDPurchases.get_all()))

        orders_count = len(orders)

        prev_page: int
        next_page: int

        if page == 0:
            prev_page = orders_count - 1
            next_page = page + 1
        elif page == orders_count - 1:
            prev_page = page - 1
            next_page = 0
        else:
            prev_page = page - 1
            next_page = page + 1

        back_ikb = InlineKeyboardButton("◀️ Назад", callback_data=admin_cb.new("Buy", "get_Buy", 0, user_id))
        prev_page_ikb = InlineKeyboardButton("←", callback_data=user_cb.new(target, action, 0, prev_page, user_id))
        check = InlineKeyboardButton("☰", callback_data=user_cb.new("Buy",
                                                                    "buyCheckApproved", bool(approved), page, user_id))
        page = InlineKeyboardButton(f"{str(page + 1)}/{str(orders_count)}",
                                    callback_data=user_cb.new("_", "_", 0, 0, 0))
        next_page_ikb = InlineKeyboardButton("→", callback_data=user_cb.new(target, action, 0, next_page, user_id))

        if orders_count == 1:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        check
                    ],
                    [
                        back_ikb
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        prev_page_ikb,
                        page, check,
                        next_page_ikb,
                    ],
                    [
                        back_ikb
                    ]
                ]
            )

    @staticmethod
    async def process_admin_profile(callback: CallbackQuery = None, message: Message = None,
                                    state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith('admin'):
                data = admin_cb.parse(callback_data=callback.data)

                if data.get("target") == "Users":

                    if data.get("action") == "get_Users":
                        try:
                            await callback.message.edit_text(text="Найти пользователя",
                                                             reply_markup=await Users.users_ikb())
                        except BadRequest:
                            await callback.message.delete()
                            await callback.message.answer(text="Найти пользователя",
                                                          reply_markup=await Users.users_ikb())

                elif data.get("target") == "Sale":
                    if data.get('action') == "get_Sale":
                        await callback.message.edit_text(text='Выберите действие!',
                                                         reply_markup=await Users.sales_ikb())

                elif data.get("target") == "Buy":
                    if data.get('action') == "get_Buy":
                        await callback.message.edit_text(text='Выберите действие!',
                                                         reply_markup=await Users.buy_ikb())

            elif callback.data.startswith('user'):
                data = user_cb.parse(callback_data=callback.data)

                if data.get("target") == "MainMenu":
                    await callback.message.edit_text(text="Админ панель",
                                                     reply_markup=await AdminForm.start_ikb())

                # Главная страница для кнопки "Пользователи"
                if data.get("target") == "User":
                    if data.get("action") == "get_User":
                        try:
                            await callback.message.edit_text(text="Найти пользователя",
                                                             reply_markup=await Users.users_ikb())
                        except BadRequest:
                            await callback.message.delete()
                            await callback.message.answer(text="Найти пользователя",
                                                          reply_markup=await Users.users_ikb())

                # Поиск пользователя по id
                elif data.get("target") == "UsersId":

                    # Поиск по id
                    if data.get("action") == "get_UsersId":
                        await callback.message.edit_text(text="Введите id Пользователя",
                                                         reply_markup=await Users.back_ikb(target="Users",
                                                                                           action="get_Users")
                                                         )
                        await AdminState.UsersId.set()

                    elif data.get('action') == "Buying":
                        user_id = int(data.get('id'))
                        user = await CRUDUsers.get(user_id=user_id)
                        buy = await CRUDPurchases.get_all(user_id=user.id)
                        if buy:
                            status = "✅ Одобрена" if buy[0].status else "❌ Не одобрена"

                            text = f"Количество заявок на покупку {len(buy)}\n" \
                                   f"Заявка № {buy[0].purchase_id}\n\n" \
                                   f"Дата {buy[0].date}\n" \
                                   f"Покупка: {buy[0].coin} - {buy[0].quantity}\n" \
                                   f"Заплатил: {buy[0].currency} - {buy[0].price_per_unit}\n\n" \
                                   f"Кошелек: {buy[0].wallet}\n\n" \
                                   f"Статус: {status}"

                            await callback.message.edit_text(text=text,
                                                             reply_markup=await Users.pagination_bue_ikb(
                                                                 target="UsersId",
                                                                 user_id=user.id,
                                                                 action="Buying_pagination"))
                        else:
                            await callback.message.edit_text(text="Ничего не нашел с таким пользователем")

                    elif data.get('action') == "Buying_pagination":
                        user_id = int(data.get('editId'))
                        page = int(data.get('id'))
                        buy = await CRUDPurchases.get_all(user_id=user_id)

                        status = "✅ Одобрена" if buy[page].status else "❌ Не одобрена"

                        text = f"Количество заявок на покупку {len(buy)}\n" \
                               f"Заявка № {buy[page].purchase_id}\n\n" \
                               f"Дата {buy[page].date}\n" \
                               f"Покупка: {buy[page].coin} - {buy[page].quantity}\n" \
                               f"Заплатил: {buy[page].currency} - {buy[page].price_per_unit}\n\n" \
                               f"Кошелек: {buy[page].wallet}\n\n" \
                               f"Статус: {status}"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await Users.pagination_bue_ikb(
                                                             target="UsersId",
                                                             user_id=user_id,
                                                             page=page,
                                                             action="Buying_pagination"))

                    elif data.get('action') == "Sale":
                        user_id = int(data.get('id'))
                        user = await CRUDUsers.get(user_id=user_id)
                        salle = await CRUDSales.get_all(user_id=user.id)

                        if salle:
                            status = "✅ Одобрена" if salle[0].status else "❌ Не одобрена"

                            text = f"Количество заявок на покупку {len(salle)}\n" \
                                   f"Заявка № {salle[0].purchase_id}\n\n" \
                                   f"Дата {salle[0].date}\n" \
                                   f"Продал: {salle[0].currency} - {salle[0].price_per_unit}\n" \
                                   f"Заплатил: {salle[0].coin} - {salle[0].quantity}\n\n" \
                                   f"ЕРИП: {salle[0].erip}\n\n" \
                                   f"Статус: {status}"

                            await callback.message.edit_text(text=text,
                                                             reply_markup=await Users.pagination_bue_ikb(
                                                                 target="UsersId",
                                                                 user_id=user.id,
                                                                 action="Buying_pagination"))
                        else:
                            await callback.message.edit_text(text="Ничего не нашел с таким пользователем")

                    elif data.get("action") == "get_check_buy":
                        page = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        user = await CRUDUsers.get(id=get_user_id)
                        transaction = await CRUDPurchases.get_all(user_id=user.id)
                        if transaction:
                            text = f"text tut"

                            await state.update_data(id=get_user_id)
                            await state.update_data(page=page)
                            await state.update_data(check_number=False)

                            if transaction[page].purchase_id != "None":
                                try:
                                    await callback.message.delete()
                                    photo = open(f'user_check/{transaction[page].purchase_id}_{user.user_id}.jpg', 'rb')
                                    await bot.send_photo(chat_id=callback.from_user.id, photo=photo,
                                                         caption=f"<i>Сделка пользователя</i>\n\n"
                                                                 f"{text}",
                                                         reply_markup=await Users.check_confirmation_ikb(
                                                             page=page,
                                                             user_id=user.id,
                                                             target="UsersId",
                                                             action_back="pagination_user_transaction",
                                                             action_confirm="Confirmation_Transaction")
                                                         )
                                    pass
                                except FileNotFoundError:
                                    pass
                            else:
                                await callback.message.edit_text(text=f"<i>Сделка пользователя</i>\n\n"
                                                                      f"Пользователь не добавил чек\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await Users.check_confirmation_ikb(
                                                                     page=page,
                                                                     user_id=user.id,
                                                                     target="UsersId",
                                                                     action_back="pagination_user_transaction",
                                                                     action_confirm="Confirmation_Transaction")
                                                                 )
                        else:
                            await callback.message.edit_text(text="Не найдено",
                                                             reply_markup=await Users.back_ikb(target="Users",
                                                                                               action="get_Users")
                                                             )

                elif data.get('target') == "Sale":
                    if data.get('action') == "SaleTrue":
                        salesTrue = list(filter(lambda x: x.status, await CRUDSales.get_all()))

                        if salesTrue:
                            user = await CRUDUsers.get(id=salesTrue[0].user_id)
                            text = f"Заявка № {salesTrue[0].sale_id}\n\n" \
                                   f"Пользователь id {user}\n" \
                                   f"Продает {salesTrue[0].coin} - {salesTrue[0].quantity}\n" \
                                   f"Нужно перевести {salesTrue[0].price_per_unit} - {salesTrue[0].currency}\n\n" \
                                   f"ЕРИП - {salesTrue[0].erip}\n" \
                                   f"Дата создания заявки - {salesTrue[0].date}"
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await Users.pagination_sales_ikb(
                                                                 target="Sale",
                                                                 user_id=user.user_id,
                                                                 action="SaleTruePagination",
                                                                 getSale=True
                                                             ))
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Sale",
                                                                                               action="get_Sale"))

                    elif data.get('action') == "SaleTruePagination":
                        page = int(data.get('id'))
                        salesTrue = list(filter(lambda x: x.status, await CRUDSales.get_all()))

                        if salesTrue:
                            user = await CRUDUsers.get(id=salesTrue[page].user_id)
                            getDate = salesTrue[page].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № {salesTrue[page].sale_id}\n\n" \
                                   f"Пользователь id {user.user_id}\n" \
                                   f"Продает {salesTrue[page].coin} - {salesTrue[page].quantity}\n" \
                                   f"Нужно перевести {salesTrue[page].price_per_unit} - {salesTrue[page].currency}\n\n" \
                                   f"ЕРИП - {salesTrue[page].erip}\n" \
                                   f"Дата создания заявки - {getDate}"
                            await callback.message.delete()
                            await callback.message.answer(text=text,
                                                          reply_markup=await Users.pagination_sales_ikb(
                                                              target="Sale",
                                                              user_id=user.user_id,
                                                              action="SaleTruePagination",
                                                              getSale=True,
                                                              page=page)
                                                          )
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Sale",
                                                                                               action="get_Sale"))

                    elif data.get('action') == "SaleFalse":
                        salesFalse = list(filter(lambda x: x.status == False, await CRUDSales.get_all()))

                        if salesFalse:
                            user = await CRUDUsers.get(id=salesFalse[0].user_id)
                            getDate = salesFalse[0].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № {salesFalse[0].sale_id}\n\n" \
                                   f"Пользователь id {user.user_id}\n" \
                                   f"Продает {salesFalse[0].coin} - {salesFalse[0].quantity}\n" \
                                   f"Нужно перевести {salesFalse[0].price_per_unit} - {salesFalse[0].currency}\n\n" \
                                   f"ЕРИП - {salesFalse[0].erip}\n" \
                                   f"Дата создания заявки - {getDate}"
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await Users.pagination_sales_ikb(
                                                                 target="Sale",
                                                                 user_id=user.user_id,
                                                                 action="SaleFalsePagination"
                                                             ))
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Sale",
                                                                                               action="get_Sale"))

                    elif data.get('action') == "SaleFalsePagination":
                        page = int(data.get('id'))
                        salesFalse = list(filter(lambda x: x.status == False, await CRUDSales.get_all()))

                        if salesFalse:
                            user = await CRUDUsers.get(id=salesFalse[page].user_id)
                            getDate = salesFalse[page].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № {salesFalse[page].sale_id}\n\n" \
                                   f"Пользователь id {user.user_id}\n" \
                                   f"Продает {salesFalse[page].coin} - {salesFalse[page].quantity}\n" \
                                   f"Нужно перевести {salesFalse[page].price_per_unit} - {salesFalse[page].currency}\n\n" \
                                   f"ЕРИП - {salesFalse[page].erip}\n" \
                                   f"Дата создания заявки - {getDate}"
                            await callback.message.delete()
                            await callback.message.answer(text=text,
                                                             reply_markup=await Users.pagination_sales_ikb(
                                                                 target="Sale",
                                                                 user_id=user.user_id,
                                                                 action="SaleFalsePagination",
                                                                 page=page))
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Sale",
                                                                                               action="get_Sale"))

                    elif data.get("action") == "saleCheckApproved":
                        page = int(data.get('id'))
                        approved = data.get('pagination')
                        get_user_id = int(data.get('editId'))

                        if approved == "False":
                            sales = list(filter(lambda x: x.status == False, await CRUDSales.get_all()))
                            action_back = "SaleFalsePagination"
                            getSale = False
                        else:
                            sales = list(filter(lambda x: x.status, await CRUDSales.get_all()))
                            action_back = "SaleTruePagination"
                            getSale = True

                        if sales:
                            user = await CRUDUsers.get(id=sales[page].user_id)
                            getDate = sales[page].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № {sales[page].sale_id}\n\n" \
                                   f"Пользователь id {user.user_id}\n" \
                                   f"Продает {sales[page].coin} - {sales[page].quantity}\n" \
                                   f"Нужно перевести {sales[page].price_per_unit} - {sales[page].currency}\n\n" \
                                   f"ЕРИП - {sales[page].erip}\n" \
                                   f"Дата создания заявки - {getDate}"
                            try:
                                await callback.message.delete()
                                photo = open(f'user_check/{sales[page].sale_id}_{get_user_id}.jpg', 'rb')
                                await bot.send_photo(chat_id=callback.from_user.id, photo=photo,
                                                     caption=f"<i>Сделка пользователя</i>\n\n"
                                                             f"{text}",
                                                     reply_markup=await Users.check_confirmation_ikb(
                                                         page=page,
                                                         sale_id=sales[page].id,
                                                         user_id=user.id,
                                                         target="Sale",
                                                         getSale=getSale,
                                                         action_back=action_back,
                                                         action_confirm="SaleApproved")
                                                     )
                            except FileNotFoundError:
                                pass

                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Sale",
                                                                                               action="get_Sale"))

                    elif data.get("action") == "SaleApproved":
                        sale_id = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        sale = await CRUDSales.get(id=sale_id)
                        sale.status = True
                        await CRUDSales.update(sale=sale)
                        user = await CRUDUsers.get(id=get_user_id)
                        text = f"Вы успешно одобрили сделку пользователю {user.user_id}"

                        await callback.message.delete()
                        await callback.message.answer(text=text,
                                                      reply_markup=await AdminForm.start_ikb())

                        admin = callback.from_user.username
                        Username = f"@{admin}" if admin != "" else f"_Администратор"

                        getDate = sale.date.strftime('%Y-%m-%d %H:%M')

                        textApproved = f"✅ Вам одобрили сделку № {sale.sale_id}\n\n" \
                                       f"Администратор :{Username}\n" \
                                       f"Продажа: {sale.coin} - {sale.quantity}\n"\
                                       f"Покупка: {sale.price_per_unit} - {sale.currency}\n"\
                                       f"ЕРИП: {sale.erip}\n\n"\
                                       f"Дата создания заявки: {getDate}"\

                        await bot.send_message(chat_id=user.user_id, text=textApproved)

                elif data.get('target') == "Buy":
                    if data.get('action') == "BuyTrue":
                        buyTrue = list(filter(lambda x: x.status, await CRUDPurchases.get_all()))

                        if buyTrue:
                            user = await CRUDUsers.get(id=buyTrue[0].user_id)
                            getDate = buyTrue[0].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № <code>{buyTrue[0].purchase_id}</code>\n\n" \
                                   f"Пользователь id <code>{user.user_id}</code>\n" \
                                   f"Получено <code>{buyTrue[0].price_per_unit} {buyTrue[0].currency}</code>\n" \
                                   f"Нужно отправить <code> {buyTrue[0].quantity} {buyTrue[0].coin}</code>\n\n" \
                                   f"Кошелек - <code>{buyTrue[0].wallet}</code>\n" \
                                   f"Дата создания заявки - <code>{getDate}</code>"

                            await callback.message.edit_text(text=text,
                                                             parse_mode="HTML",
                                                             reply_markup=await Users.pagination_buy_ikb(
                                                                 target="Buy",
                                                                 user_id=user.user_id,
                                                                 action="BuyTruePagination",
                                                                 getBuy=True
                                                             ))
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Buy",
                                                                                               action="get_Buy"))

                    elif data.get('action') == "BuyTruePagination":
                        page = int(data.get('id'))
                        buyTrue = list(filter(lambda x: x.status, await CRUDPurchases.get_all()))

                        if buyTrue:
                            user = await CRUDUsers.get(id=buyTrue[page].user_id)
                            getDate = buyTrue[page].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № <code>{buyTrue[page].purchase_id}</code>\n\n" \
                                   f"Пользователь id <code>{user.user_id}</code>\n" \
                                   f"Получено <code>{buyTrue[page].price_per_unit} {buyTrue[page].currency}</code>\n" \
                                   f"Нужно отправить <code> {buyTrue[page].quantity} {buyTrue[page].coin}</code>\n\n" \
                                   f"Кошелек - <code>{buyTrue[page].wallet}</code>\n" \
                                   f"Дата создания заявки - <code>{getDate}</code>"
                            await callback.message.delete()
                            await callback.message.answer(text=text,
                                                          reply_markup=await Users.pagination_buy_ikb(
                                                              target="Buy",
                                                              user_id=user.user_id,
                                                              action="BuyTruePagination",
                                                              getBuy=True,
                                                              page=page)
                                                          )
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Buy",
                                                                                               action="get_Buy"))

                    elif data.get('action') == "BuyFalse":
                        buyTrue = list(filter(lambda x: x.status == False, await CRUDPurchases.get_all()))

                        if buyTrue:
                            user = await CRUDUsers.get(id=buyTrue[0].user_id)
                            getDate = buyTrue[0].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № <code>{buyTrue[0].purchase_id}</code>\n\n" \
                                   f"Пользователь id <code>{user.user_id}</code>\n" \
                                   f"Получено <code>{buyTrue[0].price_per_unit} {buyTrue[0].currency}</code>\n" \
                                   f"Нужно отправить <code> {buyTrue[0].quantity} {buyTrue[0].coin}</code>\n\n" \
                                   f"Кошелек - <code>{buyTrue[0].wallet}</code>\n" \
                                   f"Дата создания заявки - <code>{getDate}</code>"

                            await callback.message.edit_text(text=text,
                                                             parse_mode="HTML",
                                                             reply_markup=await Users.pagination_buy_ikb(
                                                                 target="Buy",
                                                                 user_id=user.user_id,
                                                                 action="BuyFalsePagination",
                                                             ))
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Buy",
                                                                                               action="get_Buy"))

                    elif data.get('action') == "BuyFalsePagination":
                        page = int(data.get('id'))
                        buyTrue = list(filter(lambda x: x.status == False, await CRUDPurchases.get_all()))

                        if buyTrue:
                            user = await CRUDUsers.get(id=buyTrue[page].user_id)
                            getDate = buyTrue[page].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № <code>{buyTrue[page].purchase_id}</code>\n\n" \
                                   f"Пользователь id <code>{user.user_id}</code>\n" \
                                   f"Получено <code>{buyTrue[page].price_per_unit} {buyTrue[page].currency}</code>\n" \
                                   f"Нужно отправить <code> {buyTrue[page].quantity} {buyTrue[page].coin}</code>\n\n" \
                                   f"Кошелек - <code>{buyTrue[page].wallet}</code>\n" \
                                   f"Дата создания заявки - <code>{getDate}</code>"
                            await callback.message.delete()
                            await callback.message.answer(text=text,
                                                          reply_markup=await Users.pagination_buy_ikb(
                                                              target="Buy",
                                                              user_id=user.user_id,
                                                              action="BuyFalsePagination",
                                                              page=page)
                                                          )
                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Buy",
                                                                                               action="get_Buy"))

                    elif data.get("action") == "buyCheckApproved":
                        page = int(data.get('id'))
                        approved = data.get('pagination')
                        get_user_id = int(data.get('editId'))

                        if approved == "False":
                            buys = list(filter(lambda x: x.status == False, await CRUDPurchases.get_all()))
                            action_back = "BuyFalsePagination"
                            getBuy = False
                        else:
                            buys = list(filter(lambda x: x.status, await CRUDPurchases.get_all()))
                            action_back = "BuyTruePagination"
                            getBuy = True

                        if buys:
                            user = await CRUDUsers.get(id=buys[page].user_id)
                            getDate = buys[page].date.strftime('%Y-%m-%d %H:%M')

                            text = f"Заявка № <code>{buys[page].purchase_id}</code>\n\n" \
                                   f"Пользователь id <code>{user.user_id}</code>\n" \
                                   f"Получено <code>{buys[page].price_per_unit} {buys[page].currency}</code>\n" \
                                   f"Нужно отправить <code> {buys[page].quantity} {buys[page].coin}</code>\n\n" \
                                   f"Кошелек - <code>{buys[page].wallet}</code>\n" \
                                   f"Дата создания заявки - <code>{getDate}</code>"
                            try:
                                await callback.message.delete()
                                photo = open(f'user_check/{buys[page].purchase_id}_{get_user_id}.jpg', 'rb')
                                await bot.send_photo(chat_id=callback.from_user.id, photo=photo,
                                                     caption=f"<i>Сделка пользователя</i>\n\n"
                                                             f"{text}",
                                                     reply_markup=await Users.check_confirmation_ikb(
                                                         page=page,
                                                         sale_id=buys[page].id,
                                                         user_id=user.id,
                                                         target="Buy",
                                                         getSale=getBuy,
                                                         action_back=action_back,
                                                         action_confirm="BuyApproved")
                                                     )
                            except FileNotFoundError:
                                pass

                        else:
                            await callback.message.edit_text(text="Не найдено!",
                                                             reply_markup=await Users.back_ikb(target="Buy",
                                                                                               action="get_Buy"))

                    elif data.get("action") == "BuyApproved":
                        purchase_id = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        purchase = await CRUDPurchases.get(id=purchase_id)
                        purchase.status = True
                        await CRUDPurchases.update(purchase=purchase)

                        user = await CRUDUsers.get(id=get_user_id)
                        text = f"Вы успешно одобрили сделку пользователю <code>{user.user_id}</code>"

                        await callback.message.delete()
                        await callback.message.answer(text=text,
                                                      parse_mode="HTML",
                                                      reply_markup=await AdminForm.start_ikb())

                        admin = callback.from_user.username
                        Username = f"@{admin}" if admin != "" else f"_Администратор"

                        getDate = purchase.date.strftime('%Y-%m-%d %H:%M')

                        textApproved = f"✅ Вам одобрили сделку № <code>{purchase.purchase_id}</code>\n\n" \
                                       f"Администратор :{Username}\n" \
                                       f"Продажа: <code>{purchase.price_per_unit} {purchase.currency}</code>\n"\
                                       f"Покупка: <code>{purchase.quantity} {purchase.coin}</code>\n"\
                                       f"Кошелек - <code>{purchase.wallet}</code>\n\n"\
                                       f"Дата создания заявки: {getDate}"\

                        await bot.send_message(chat_id=user.user_id, text=textApproved, parse_mode="HTML")

        if message:
            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=message.message_id - 1
                )
            except BadRequest:
                pass

            if state:

                if await state.get_state() == "AdminState:UsersId":
                    if message.text.isdigit():
                        user = await CRUDUsers.get(user_id=int(message.text))
                        if user:
                            await message.answer(text="Выберите категорию",
                                                 reply_markup=await Users.sell_or_buy_ikb(user_id=int(message.text)))
                            await state.finish()
                        else:
                            await message.answer(text="Не найдено")
                            await state.finish()
                    else:
                        await message.answer(text="Доступен ввод только цифр")
                        await AdminState.UsersId.set()
