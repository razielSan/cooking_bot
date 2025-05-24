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


def generate_main_menu():
    """ Кнопки основного меню """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="✅ Сделать заказ"),
            ],
            [
                KeyboardButton(text="📓 История"),
                KeyboardButton(text="🚃 Корзина"),
                KeyboardButton(text="🔨 Настройки"),
            ]
        ]
    )

    return keyboard


def back_to_main_menu():
    """ Кнопка главного меню """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="Главное меню"),
            ],
        ]
    )
    return keyboard


def back_arrow_button():
    """ Кнопка назад """
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👈 Назад")
            ]
        ]
    )

    return reply_kb