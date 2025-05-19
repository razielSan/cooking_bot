from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    """Старт бота"""
    await message.answer(
        f"Здравствуйте, <b>{message.from_user.full_name}</b>\n"
        f"Вас привествует служба доставки планеты Земля",
        parse_mode="HTML"
    )


@router.message()
async def echo_handler(message: Message):
    await message.answer(text=message.text)
