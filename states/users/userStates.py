from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    Buy = State()
    Wallet = State()
    UserPhoto = State()
    ERIP = State()
