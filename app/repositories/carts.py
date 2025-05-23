from sqlalchemy import DECIMAL, select, update

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

    def update_to_cart(self, price: DECIMAL, cart_id: int, quantity=1):
        """Обновление данных временной корзины"""
        with db_helper.get_session() as session:
            # query = (
            #     update(self.model)
            #     .where(
            #         self.model.id == cart_id,
            #     )
            #     .values(
            #         total_price=price,
            #         total_products=quantity,
            #     )
            # )
            # session.execute(query) # Один из способ Обновления

            session.query(self.model).filter_by(id=cart_id).update(
                values={
                    "total_price": price,
                    "total_products": quantity,
                }
            )
            session.commit()
