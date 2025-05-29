from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from repositories.categories import CategoriesSQLAlchemyRepository
from repositories.products import ProductsSQLAlchemyRepository
from repositories.carts import CartsSQLAlchemyRepository
from repositories.finally_carts import FinallyCartsSQLAlchemyRepository


def generate_category_menu(chat_id: int):
    categories = CategoriesSQLAlchemyRepository().get_all_categories()

    price = (
        FinallyCartsSQLAlchemyRepository().get_total_price_product_or_all_carts_product(
            chat_id=chat_id,
        )
    )
    total_price = price if price else 0

    inline_kb = InlineKeyboardBuilder()
    inline_kb.button(
        text=f"Ваша корзина: ({total_price} сум)",
        callback_data="Ваша корзина",
    )
    for category in categories:
        inline_kb.button(
            text=f"{category.category_name}",
            callback_data=f"category_{category.id}",
        )
    inline_kb.adjust(1, 2)
    return inline_kb.as_markup(resize_keyboard=True)


def show_product_by_category(category_id: int):
    """Кнопки продуктов"""
    products = ProductsSQLAlchemyRepository().get_all_product_by_category(
        category_id=category_id,
    )
    inline_kb = InlineKeyboardBuilder()
    for product in products:
        inline_kb.button(
            text=product.product_name,
            callback_data=f"product_{product.id}",
        )
    inline_kb.adjust(2)
    inline_kb.row(
        InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="return_to_category",
        )
    )
    return inline_kb.as_markup()


def generate_constructor_button(quantity=1, product_name=""):
    """Кнопки выбора количества продуктов"""
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👎 -1", callback_data=f"action_-_{product_name}"
                ),
                InlineKeyboardButton(text=str(quantity), callback_data="quantity"),
                InlineKeyboardButton(
                    text="👍 +1", callback_data=f"action_+_{product_name}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Положить в корзину",
                    callback_data=f"Положить в корзину",
                )
            ],
        ]
    )

    return inline_kb
    # inline_kb = InlineKeyboardBuilder()
    # inline_kb.button(text="👎 -1", callback_data="ProductsQuantity_-1")
    # inline_kb.button(text="1", callback_data="quantity")
    # inline_kb.button(text="👍 +1", callback_data="ProductsQuantity_1")
    # return inline_kb.as_markup()


def generate_finally_carts_products(list_product_name, cart_id: int):
    """Отображение кнопок финальной корзины"""
    inline_kb = InlineKeyboardBuilder()
    len_list_product_name = len(list_product_name)
    inline_kb.row(
        InlineKeyboardButton(
            text="☕ Оформить заказ",
            callback_data="payment",
        )
    )
    for product_name in list_product_name:
        inline_kb.button(
            text="➖",
            callback_data=f"CartAction_-_{product_name}",
        ),
        inline_kb.button(
            text=f"❌ {product_name}", callback_data=f"delete_{product_name}_{cart_id}"
        ),
        inline_kb.button(text="➕", callback_data=f"CartAction_+_{product_name}"),

    total_list = [3 for _ in range(len_list_product_name)]
    total_list.insert(0, 1)
    inline_kb.adjust(*total_list)
    return inline_kb.as_markup()
