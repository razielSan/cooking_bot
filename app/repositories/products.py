from database.db_helper import db_helper
from database import Products


class ProductsSQLAlchemyRepository:
    model = Products

    def get_all_products_from_category(self, category_id: int):
        """ Получаем продукты категории по id категории """
        with db_helper.get_session() as session:
            products = session.query(Products).filter_by(
                category_id=category_id,
            ).all()

            return products
