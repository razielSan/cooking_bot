from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest

from repositories.users import UsersSQLAlchemyRepository
from repositories.carts import CartsSQLAlchemyRepository
from repositories.categories import CategoriesSQLAlchemyRepository
from repositories.products import ProductsSQLAlchemyRepository
from keyboards.reply import (
    share_phone_button,
    back_to_main_menu,
    back_arrow_button,
)
from keyboards.inline import (
    generate_category_menu,
    show_product_by_category,
    generate_constructor_button,
)
from functions import get_user_register, show_main_menu, get_text_for_product
from extensions import bot
from database.db_helper import db_helper


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
    product = ProductsSQLAlchemyRepository().get_product_by_data(
        id=product_id,
    )

    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    if user_cart := CartsSQLAlchemyRepository().get_user_cart(chat_id=chat_id):
        CartsSQLAlchemyRepository().update_to_cart(
            price=product.price,
            cart_id=user_cart.id,
        )

        await bot.send_photo(
            chat_id=chat_id,
            photo=FSInputFile(path=product.image),
            caption=get_text_for_product(
                price=product.price,
                product_name=product.product_name,
                description=product.description,
            ),
            parse_mode="HTML",
            reply_markup=generate_constructor_button(
                product_name=product.product_name,
            )
        )
        # await bot.send_message(
        #     text="Выберите количество товара",
        #     chat_id=chat_id,
        #     reply_markup=generate_constructor_button(
        #         product_name=product.product_name,
        #     ),
        # )

        await bot.send_message(
            chat_id=chat_id,
            text="Вернуться назад",
            reply_markup=back_arrow_button(),
        )

    else:
        await bot.send_message(
            chat_id=chat_id,
            text="К сожалению у нас нет вашего контакта",
            reply_markup=share_phone_button(),
        )


@router.message(F.text == "👈 Назад")
async def return_to_category_menu(message: Message):
    """Назад к выбору продукта по категории"""
    chat_id = message.chat.id
    message_id = message.message_id
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id - 1,
    )

    await make_order(message)


@router.callback_query(F.data.contains("action_"))
async def constructor_change(call: CallbackQuery):
    """Логика конструктора"""
    chat_id = call.from_user.id
    message_id = call.message.message_id
    _, action, product_name = call.data.split("_")
    user_cart = CartsSQLAlchemyRepository().get_user_cart(chat_id=chat_id)
    product = ProductsSQLAlchemyRepository().get_product_by_data(
        product_name=product_name,
    )
    print(product_name, "2" * 20)
    price = product.price

    print(action)
    if action == "+":
        user_cart.total_products += 1
    elif action == "-":
        print("-" * 20)
        if user_cart.total_products < 2:
            print("Hello")
            await call.answer("Меньше одного нельзя")
        else:
            user_cart.total_products -= 1
    if user_cart.total_products >= 1:
        price = price * user_cart.total_products
        CartsSQLAlchemyRepository().update_to_cart(
            price=price,
            cart_id=user_cart.id,
            quantity=user_cart.total_products,
        )

        try:
            text = get_text_for_product(
                price=price,
                product_name=product.product_name,
                description=product.description,
            )

            await bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=FSInputFile(path=product.image),
                    caption=text,
                    parse_mode="HTML",
                ),
                reply_markup=generate_constructor_button(
                    quantity=user_cart.total_products,
                    product_name=product.product_name,
                ),
            )

        except TelegramBadRequest as err:
            print(err)
