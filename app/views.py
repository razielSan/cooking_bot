from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from repositories.users import UsersSQLAlchemyRepository
from repositories.carts import CartsSQLAlchemyRepository
from keyboards.reply import share_phone_button


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    """Старт бота"""
    await message.answer(
        f"Здравствуйте, <b>{message.from_user.full_name}</b>\n"
        f"Вас привествует служба доставки планеты Земля",
        parse_mode="HTML",
    )

    await get_user_register(message)


async def get_user_register(message: Message):
    """Первая регистрация пользователя  с проверкой на существование"""

    name = message.from_user.full_name
    telegram = message.chat.id
    result = UsersSQLAlchemyRepository().register_user(
        name=name,
        telegram=telegram,
    )
    if result:
        await message.answer("Авторизация прошла успешно")
        # TODO показать меню
    else:
        await message.answer(
            text="Для связи с вами нужен ваш контакт",
            reply_markup=share_phone_button(),
        )


@router.message(F.contact)
async def update_user_info_finish_register(message: Message):
    """Обновление данных пользователя его контактам"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    UsersSQLAlchemyRepository().add_phone_user(
        telegram=chat_id,
        phone=phone,
    )
    if CartsSQLAlchemyRepository().create_user_cart(chat_id=chat_id):
        await message.answer(text="Регистрация прошла успешно")