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
