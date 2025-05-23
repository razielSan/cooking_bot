from sqlalchemy import DECIMAL, select

from database import Carts, Users
from database.db_helper import db_helper


class CartsSQLAlchemyRepository:
    model = Carts

    def create_user_cart(self, chat_id: int):
        """Создание временной коризны пользователя"""
        with db_helper.get_session() as session:
            try:
                # один из способов запроса

                # user = session.scalar(
                #     select(Users).where(
                #         Users.telegram == chat_id,
                #     )
                # )
                user = (
                    session.query(Users)
                    .filter_by(
                        telegram=chat_id,
                    )
                    .first()
                )
                carts = self.model(
                    user_id=user.id,
                )
                session.add(carts)
                session.commit()
                return True
            except Exception as err:
                print(err)
                session.rollback()
                return False

    def get_user_cart(self, chat_id: int):
        """Получаем id корзины по связанной таблице Users"""
        with db_helper.get_session() as session:
            # users = session.query(Users).filter_by(telegram=chat_id).first()
            # carts_id = users.carts.id # запрос через relationship

            query = (
                select(self.model.id)
                .join(Users)
                .where(
                    Users.telegram == chat_id,
                )
            )

            carts_id = session.scalar(query)
            return carts_id

    def update_to_cart(self, price: DECIMAL, cart_id: int, quantity=1,):
        pass