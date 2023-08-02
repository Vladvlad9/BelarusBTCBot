import random
import string

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from config.config import CONFIGTEXT
from crud import CRUDUsers
from handlers.users.Cryptocurrency import Cryptocurrency
from keyboards.inline.users.mainFormIkb import main_cb, MainForms
from loader import dp, bot
from schemas import UserSchema
from states.users.userStates import UserStates

from captcha.image import ImageCaptcha
from random import choice
from PIL import ImageFont, ImageDraw, Image


async def create_captcha(text: str) -> str:
    image = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('font/arial.ttf', size=30)
    draw.text((50, 25), text, font=font, fill='black')

    file_path = 'captcha.png'
    image.save(file_path)
    return file_path


async def get_captcha() -> dict:
    captcha_text = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
    file_path = await create_captcha(captcha_text)
    return {"captcha_text": captcha_text, "file_path": file_path}


@dp.message_handler(commands=["start"], state=UserStates.all_states)
async def registration_starts_state(message: types.Message, state: FSMContext):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        if user.check_captcha:
            await state.finish()
            await message.delete()
            await message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT, reply_markup=await MainForms.main_kb())
        else:
            captcha = await get_captcha()
            await message.answer(text="Капча введена неверно, попробуйте еще раз")
            await bot.send_photo(message.chat.id, open(captcha["file_path"], 'rb'))
            await UserStates.Captcha.set()
    else:
        await message.answer(text="что то я тебя не знаю!")


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        if user.check_captcha:
            await message.delete()
            await message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                                 reply_markup=await MainForms.main_kb())
        else:
            captcha = await get_captcha()
            await UserStates.Captcha.set()
            await bot.send_photo(chat_id=message.chat.id,
                                 photo=open(captcha["file_path"], 'rb'),
                                 caption="В целях безопасности🔐 \n"
                                         "Подтвердить что вы не бот😎✅, чтобы пользоваться ресурсом 🤖Bot🤖\n"
                                         "Введите символы с картинки")
    else:
        captcha = await get_captcha()

        await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id,
                                            captcha=captcha["captcha_text"]))
        await UserStates.Captcha.set()
        await bot.send_photo(chat_id=message.chat.id,
                             photo=open(captcha["file_path"], 'rb'),
                             caption="В целях безопасности🔐 \n"
                                     "Подтвердить что вы не бот😎✅, чтобы пользоваться ресурсом 🤖Bot🤖\n"
                                     "Введите символы с картинки")


@dp.message_handler(text="Купить 💰")
async def Buy(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        if user.check_captcha:
            text = "Выберите валюту которую вы хотите купить."
            await message.delete()
            await message.answer(text=text,
                                 reply_markup=await MainForms.coin_ikb(target="Buy",
                                                                       action="coin_buy")
                                 )
        else:
            captcha = await MainForms.get_captcha()
            user.captcha = captcha['captcha_text']
            await CRUDUsers.update(user=user)

            await bot.send_photo(chat_id=message.chat.id,
                                 photo=open(captcha["file_path"], 'rb'))

            await bot.send_message(chat_id=message.chat.id,
                                   text="В целях безопасности🔐 \n"
                                        "Подтвердить что вы не бот😎✅, "
                                        "чтобы пользоваться ресурсом 🤖Bot🤖\n"
                                        "Введите символы с картинки")

            await UserStates.Captcha.set()

    else:
        await message.answer(text='Я тебя не знаю!')


@dp.message_handler(text="Продать 📈")
async def Sell(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        if user.check_captcha:
            text = "Выберите валюту которую вы хотите продать."
            await message.delete()
            await message.answer(text=text,
                                 reply_markup=await MainForms.coin_ikb(target="Sell",
                                                                       action="coin_buy")
                                 )
        else:
            captcha = await MainForms.get_captcha()
            user.captcha = captcha['captcha_text']
            await CRUDUsers.update(user=user)

            await bot.send_photo(chat_id=message.chat.id,
                                 photo=open(captcha["file_path"], 'rb'))

            await bot.send_message(chat_id=message.chat.id,
                                   text="В целях безопасности🔐 \n"
                                        "Подтвердить что вы не бот😎✅, "
                                        "чтобы пользоваться ресурсом 🤖Bot🤖\n"
                                        "Введите символы с картинки")

            await UserStates.Captcha.set()

    else:
        await message.answer(text='Я тебя не знаю!')


@dp.message_handler(text="Контакты 💬")
async def Contacts(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        if user.check_captcha:
            text = "Контакты"
            await message.answer(text=text,
                                 reply_markup=await MainForms.contacts_ikb())
        else:
            captcha = await MainForms.get_captcha()
            user.captcha = captcha['captcha_text']
            await CRUDUsers.update(user=user)

            await bot.send_photo(chat_id=message.chat.id,
                                 photo=open(captcha["file_path"], 'rb'))

            await bot.send_message(chat_id=message.chat.id,
                                   text="В целях безопасности🔐 \n"
                                        "Подтвердить что вы не бот😎✅, "
                                        "чтобы пользоваться ресурсом 🤖Bot🤖\n"
                                        "Введите символы с картинки")

            await UserStates.Captcha.set()

    else:
        await message.answer(text='Я тебя не знаю!')


@dp.message_handler(state=UserStates.Captcha)
async def check_captcha(message: types.Message, state: FSMContext):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if message.text == user.captcha:
        await message.delete()
        await message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT, reply_markup=await MainForms.main_kb())
        user.check_captcha = True
        await CRUDUsers.update(user=user)
        await state.finish()
    else:
        await message.reply("Капча введена неверно, попробуйте еще раз")
        captcha = await get_captcha()
        user.captcha = captcha["captcha_text"]
        await CRUDUsers.update(user=user)
        await bot.send_photo(message.chat.id, open(captcha["file_path"], 'rb'))
        await UserStates.Captcha.set()


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForms.process(callback=callback, state=state)


@dp.message_handler(state=UserStates.all_states, content_types=["text", "photo"])
async def process_message(message: types.Message, state: FSMContext):
    await MainForms.process(message=message, state=state)