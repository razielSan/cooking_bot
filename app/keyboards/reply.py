from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def share_phone_button():
    """Кнопка для отправки контакта"""
    # builder = ReplyKeyboardBuilder(re)
    # builder.button(text="Отправить свой контакт ", request_contact=True)

    # return builder.as_markup(resize_keyboard=True)
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Отправить свой контакт ", request_contact=True)],
        ],
    )
    return keyboard
