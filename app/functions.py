from aiogram.types import Message

from repositories.users import UsersSQLAlchemyRepository
from keyboards.reply import share_phone_button, generate_main_menu


async def show_main_menu(message: Message):
    """Сделать заказ, История, Корзина, Настройки"""
    await message.answer(
        text="Выберите направление",
        reply_markup=generate_main_menu(),
    )


async def get_user_register(message: Message):
    """Первая регистрация пользователя  с проверкой на существование"""

    name = message.from_user.full_name
    telegram = message.chat.id
    result = UsersSQLAlchemyRepository().register_user(
        name=name,
        telegram=telegram,
    )
    if result:
        await message.answer(
            text="Для связи с вами нужен ваш контакт",
            reply_markup=share_phone_button(),
        )
    else:
        await message.answer("Авторизация прошла успешно")
        await show_main_menu(message)
