import random
import string

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers
from keyboards.inline.users.mainFormIkb import main_cb, MainForms
from loader import dp, bot
from schemas import UserSchema
from states.users.userStates import UserStates

from captcha.image import ImageCaptcha
from random import choice
from PIL import ImageFont, ImageDraw, Image


def create_captcha(text: str) -> str:
    image = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('font/arial.ttf', size=30)
    draw.text((50, 25), text, font=font, fill='black')

    file_path = 'captcha.png'
    image.save(file_path)
    return file_path


@dp.message_handler(commands=["start"], state=UserStates.all_states)
async def registration_starts(message: types.Message):
    await message.delete()
    await message.answer(text="Приветствие!", reply_markup=await MainForms.main_ikb())


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        await message.delete()
        await message.answer(text="Приветствие!", reply_markup=await MainForms.main_ikb())
    else:

        captcha_text = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
        file_path = create_captcha(captcha_text)

        await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id,
                                            captcha=captcha_text))

        await bot.send_photo(message.chat.id, open(file_path, 'rb'))


@dp.message_handler()
async def check_captcha(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if message.text == user.captcha:
        await message.delete()
        await message.answer(text="Приветствие!", reply_markup=await MainForms.main_ikb())
    else:
        await message.reply("Капча введена неверно, попробуйте еще раз")
        captcha_text = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
        file_path = create_captcha(captcha_text)
        user.captcha = captcha_text
        await CRUDUsers.update(user=user)
        await bot.send_photo(message.chat.id, open(file_path, 'rb'))


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForms.process(callback=callback, state=state)


@dp.message_handler(state=UserStates.all_states, content_types=["text", "photo"])
async def process_message(message: types.Message, state: FSMContext):
    await MainForms.process(message=message, state=state)