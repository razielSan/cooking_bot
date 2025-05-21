from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from repositories.users import UsersSQLAlchemyRepository
from repositories.carts import CartsSQLAlchemyRepository
from repositories.categories import CategoriesSQLAlchemyRepository
from keyboards.reply import share_phone_button, back_to_main_menu
from functions import get_user_register, show_main_menu
from extensions import bot


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


@router.message(F.contact)
async def update_user_info_finish_register(message: Message):
    """Обновление данных пользователя его контактам"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    UsersSQLAlchemyRepository().add_phone_user(
        telegram=chat_id,
        phone=phone,
    )

    user_cart = CartsSQLAlchemyRepository().create_user_cart(chat_id=chat_id)

    if user_cart:
        await message.answer(text="Регистрация прошла успешно")

    await show_main_menu(message)


@router.message(F.text == "✅ Сделать заказ")
async def make_order(message: Message):
    """Реакция на кнопку сделать заказ"""
    print(CategoriesSQLAlchemyRepository().get_all_categories())
    chat_id = message.chat.id
    # TODO Получить id корзины пользователя
    await bot.send_message(
        chat_id=chat_id,
        text="Погнали",
        reply_markup=back_to_main_menu(),
    )
    # await message.answer(
    #     text="Выберите категорию",
    #     reply_markup="",
    # )


