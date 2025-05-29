from aiogram.types import Message

from repositories.users import UsersSQLAlchemyRepository
from repositories.finally_carts import FinallyCartsSQLAlchemyRepository
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


def get_text_for_product(price: int, product_name: str, description: str):
    """Возвращает описание продукта"""
    text = (
        f"<b>{product_name}</b>\n\n"
        f"<b>Ингридиенты:</b>\n"
        f"{description}\n"
        f"<b>Цена</b>: {price} сумм"
    )
    return text


def get_show_finally_carts(chat_id: int, user_text: str, html=True):
    """ Возвращает список из имен продуктов, количество продуктов, содержимое корзины,
        общую стоимость продуктов и cart_id пользователя
    """
    list_all_cart_for_products = (
        FinallyCartsSQLAlchemyRepository().get_total_price_product_or_all_carts_product(
            chat_id=chat_id,
            order=True,
        )
    )
    count = total_price = total_products = 0
    list_product_name = []
    if list_all_cart_for_products:
        list_cart_products = [(p.product_name, p) for p in list_all_cart_for_products]
        list_cart_products.sort(key=lambda x: x[0])
        total_text = f"<b>{user_text}</b>\n\n" if html else f"{user_text}\n\n"
        for _, product in list_cart_products:
            count += 1
            total_price += product.final_price
            total_products += product.quantity

            text = (
                f"{count}. {product.product_name}\n"
                f"Количество: {product.quantity}\nСтоимость: {product.final_price}\n\n"
            )
            total_text += text
            list_product_name.append(product.product_name)

        
        total_text += f"Общее количество продуктов: {total_products}\n"
        total_text += f"Общее cтоимость продуктов: {total_price}"
        total_text += ""

        cart_id = list_all_cart_for_products[0].cart_id
        return (list_product_name, count, total_text, total_price, cart_id)
    return None
