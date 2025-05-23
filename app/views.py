from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, FSInputFile

from repositories.users import UsersSQLAlchemyRepository
from repositories.carts import CartsSQLAlchemyRepository
from repositories.categories import CategoriesSQLAlchemyRepository
from repositories.products import ProductsSQLAlchemyRepository
from keyboards.reply import share_phone_button, back_to_main_menu
from keyboards.inline import generate_category_menu, show_product_by_category
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
    await message.answer(
        text="Выберите категорию",
        reply_markup=generate_category_menu(),
    )


@router.message(F.text.regexp(r"^Г[а-я]+ м[а-я]{3}"))
async def return_to_main_menu(message: Message):
    """Реакция на кнопку главное меню"""
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id - 1,
    )

    await show_main_menu(message)


@router.callback_query(F.data.startswith("category_"))
async def show_product_button(call: CallbackQuery):
    """ " Показ всех продуктов выбранной категории"""
    chat_id = call.message.chat.id
    category_id = int(call.data.split("_")[-1])
    message_id = call.message.message_id
    await bot.edit_message_text(
        text="Выберите продукт",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=show_product_by_category(category_id),
    )


@router.callback_query(F.data == "return_to_category")
async def return_to_category(call: CallbackQuery):
    """Возврат к выбору категорий продуктов"""
    chat_id = call.message.chat.id
    mesage_id = call.message.message_id

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=mesage_id,
        text="Выберите категорию",
        reply_markup=generate_category_menu(),
    )


@router.callback_query(F.data.contains("product_"))
async def show_product_detail(call: CallbackQuery):
    """Отображение информациии о продукте"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split("_")[-1])
    product = ProductsSQLAlchemyRepository().get_product_by_id(
        product_id=product_id,
    )

    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    if user_cart_id := CartsSQLAlchemyRepository().get_user_cart(chat_id=chat_id):
        CartsSQLAlchemyRepository().update_to_cart(
            price=product.price,
            cart_id=user_cart_id,
        )

        text = (
            f"<b>{product.product_name}</b>\n\n"
            f"<b>Ингридиенты:</b>\n"
            f"{product.description}\n"
            f"<b>Цена</b>: {product.price} сумм"
        )

        await bot.send_photo(
            chat_id=chat_id,
            photo=FSInputFile(path=product.image),
            caption=text,
            parse_mode="HTML",
        )

    else:
        await bot.send_message(
            chat_id=chat_id,
            text="К сожалению у нас нет вашего контакта",
            reply_markup=share_phone_button(),
        )
