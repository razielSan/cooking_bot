from database import Categories
from database.db_helper import db_helper


class CategoriesSQLAlchemyRepository:
    model = Categories

    def get_all_categories(self):
        """ Получаем все категории """
        with db_helper.get_session() as session:
            list_categories = session.query(Categories).all()
            return list_categories