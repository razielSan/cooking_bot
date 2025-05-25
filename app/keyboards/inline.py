from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from repositories.categories import CategoriesSQLAlchemyRepository
from repositories.products import ProductsSQLAlchemyRepository


def generate_category_menu():
    categories = CategoriesSQLAlchemyRepository().get_all_categories()
    inline_kb = InlineKeyboardBuilder()
    inline_kb.button(
        text="Ваша корзина (TODO сум)",
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
                InlineKeyboardButton(text="👎 -1", callback_data=f"action_-_{product_name}"),
                InlineKeyboardButton(text=str(quantity), callback_data="quantity"),
                InlineKeyboardButton(text="👍 +1", callback_data=f"action_+_{product_name}"),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Добавить в корзину", callback_data="Добавить в корзину"
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
