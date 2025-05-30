from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    Message,
    FSInputFile,
    InputMediaPhoto,
    LabeledPrice,
)
from aiogram.exceptions import TelegramBadRequest

from repositories.users import UsersSQLAlchemyRepository
from repositories.carts import CartsSQLAlchemyRepository
from repositories.categories import CategoriesSQLAlchemyRepository
from repositories.products import ProductsSQLAlchemyRepository
from repositories.finally_carts import FinallyCartsSQLAlchemyRepository

from keyboards.reply import (
    share_phone_button,
    back_to_main_menu,
    back_arrow_button,
)
from keyboards.inline import (
    generate_category_menu,
    show_product_by_category,
    generate_constructor_button,
    generate_finally_carts_products,
)
from functions import (
    get_user_register,
    show_main_menu,
    get_text_for_product,
    get_show_finally_carts,
)
from extensions import bot
from database.db_helper import db_helper
from config.settings import settings


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
    chat_id = message.chat.id
    await bot.send_message(
        chat_id=chat_id,
        text="Погнали",
        reply_markup=back_to_main_menu(),
    )
    await message.answer(
        text="Выберите категорию",
        reply_markup=generate_category_menu(chat_id),
    )


@router.message(F.text.regexp(r"^Г[а-я]+ м[а-я]{3}"))
async def return_to_main_menu(message: Message):
    """Реакция на кнопку главное меню"""
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id - 1,
        )
    except TelegramBadRequest:
        pass

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
        reply_markup=generate_category_menu(chat_id),
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
            ),
        )
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


@router.callback_query(F.data == "Ваша корзина")
async def get_show_carts(call: CallbackQuery):
    """Отображение корзины пользователя"""
    message_id = call.message.message_id
    chat_id = call.from_user.id
    context = get_show_finally_carts(chat_id=chat_id, user_text="Ваша корзина")

    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    if context:
        list_product_name, count, text, *_, cart_id = context
        await call.message.answer(
            f"{text}",
            parse_mode="HTML",
            reply_markup=generate_finally_carts_products(
                list_product_name=list_product_name,
                cart_id=cart_id,
            ),
        )
    else:
        await call.message.answer("Корзина пуста")


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
    price = product.price
    if action == "+":
        user_cart.total_products += 1
    elif action == "-":
        if user_cart.total_products < 2:
            await call.answer("Меньше одного нельзя")
        else:
            user_cart.total_products -= 1
    if user_cart.total_products > 0:
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


@router.callback_query(F.data.contains("Положить в корзину"))
async def add_to_finally_carts(call: CallbackQuery):
    """Добавление товара в корзину"""
    chat_id = call.from_user.id
    message_id = call.message.message_id

    data = call.message.caption.split("\n")
    product_name = data[0]
    carts = CartsSQLAlchemyRepository().get_user_cart(chat_id=chat_id)

    result = FinallyCartsSQLAlchemyRepository().insert_or_update_finally_carts(
        product_name=product_name,
        final_price=carts.total_price,
        cart_id=carts.id,
        quantity=carts.total_products,
    )
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    if result:
        await call.message.answer("Продукт успешно добавленн 😊")

    else:
        await call.answer("Товар в корзине обновлен")

    await make_order(call.message)


@router.callback_query(F.data.contains("delete"))
async def delete_for_cart_products(call: CallbackQuery):
    """ Удаление продукта с финальной корзины """ ""
    _, product_name, cart_id = call.data.split("_")
    FinallyCartsSQLAlchemyRepository().delete_for_product_by_FinallyCarts(
        product_name=product_name,
        cart_id=int(cart_id),
    )
    chat_id = call.from_user.id
    message_id = call.message.message_id

    context = get_show_finally_carts(
        chat_id=chat_id,
        user_text="Ваша корзина",
    )

    if not context:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        await call.message.answer("Корзина пуста")
        await make_order(call.message)
    else:
        list_product_name, count, total_text, total_price, cart_id = context

        await bot.answer_callback_query(callback_query_id=call.id, text="Товар удаленн")

        await bot.edit_message_text(
            text=total_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=generate_finally_carts_products(
                list_product_name=list_product_name,
                cart_id=cart_id,
            ),
            parse_mode="HTML",
        )


@router.callback_query(F.data.contains("CartAction"))
async def change_finalli_carts(call: CallbackQuery):
    """Изменение количества товаров в финальной корзине"""
    _, action, product_name = call.data.split("_")
    message_id = call.message.message_id
    chat_id = call.from_user.id

    cart = CartsSQLAlchemyRepository().get_user_cart(chat_id=chat_id)
    finally_cart = FinallyCartsSQLAlchemyRepository().get_finally_cart_by_product(
        product_name=product_name,
        cart_id=cart.id,
    )

    if action == "-":
        if finally_cart.quantity == 1:
            await call.answer("Меньше одного нельзя")
        else:
            finally_cart.quantity -= 1
    elif action == "+":
        finally_cart.quantity += 1

    if finally_cart.quantity > 0:
        product = ProductsSQLAlchemyRepository().get_product_by_data(
            product_name=product_name,
        )
        finally_cart.final_price = product.price * finally_cart.quantity
        FinallyCartsSQLAlchemyRepository().insert_or_update_finally_carts(
            final_price=finally_cart.final_price,
            quantity=finally_cart.quantity,
            product_name=finally_cart.product_name,
            cart_id=cart.id,
        )

        context = get_show_finally_carts(
            chat_id=chat_id,
            user_text="Ваша корзина",
        )

        list_product_name, count, total_text, total_price, cart_id = context

        await bot.edit_message_text(
            text=total_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=generate_finally_carts_products(
                list_product_name=list_product_name,
                cart_id=cart.id,
            ),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "payment")
async def payment_for_the_order(call: CallbackQuery):
    """Оплата заказа"""
    chat_id = call.from_user.id
    message_id = call.message.message_id

    list_product_name, count, total_text, total_price, cart_id = get_show_finally_carts(
        chat_id=chat_id,
        user_text="Итоговый список для оплаты",
        html=False,
    )

    total_text += "\nДоставка по городу 1000 сумм"
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    await bot.send_invoice(
        chat_id=chat_id,
        title="Ваш заказ",
        description=total_text,
        payload="bot-defined invoice payload",
        provider_token=settings.PAYMENT_TOKEN,
        currency="UZS",
        prices=[
            LabeledPrice(
                label="Общая стоимость",
                amount=int(total_price * 100),
            ),
            LabeledPrice(
                label="Доставка",
                amount=1000,
            ),
        ],
    )

    await bot.send_message(
        chat_id=chat_id,
        text="Заказ оплаченн",
    )

    FinallyCartsSQLAlchemyRepository().delete_for_all_products_by_cart_id(
        cart_id=cart_id,
    )

    await sending_report_message(
        chat_id=chat_id,
        text=total_text,
    )


async def sending_report_message(chat_id: int, text: str):
    user = UsersSQLAlchemyRepository().get_user_info(chat_id=chat_id)
    text += f"\n\nИмя заказчика: {user.name}\nКонтактный номер: {user.phone}"
    await bot.send_message(
        chat_id=settings.MANAGER,
        text=text,
    )
