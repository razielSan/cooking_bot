from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy import select

from database import Finally_carts, Carts, Users
from database.db_helper import db_helper


class FinallyCartsSQLAlchemyRepository:
    model = Finally_carts

    def insert_or_update_finally_carts(
        self,
        product_name: str,
        final_price: float,
        quantity: str,
        cart_id: int,
    ):
        """Вносим новую запись либо редактируем существующую если такой продукт уже есть"""
        with db_helper.get_session() as session:
            try:
                finaly_carts = self.model(
                    cart_id=cart_id,
                    final_price=final_price,
                    quantity=quantity,
                    product_name=product_name,
                )
                session.add(finaly_carts)
                session.commit()
                return True
            except IntegrityError:
                session.rollback()

                carts = (
                    session.query(self.model)
                    .filter_by(
                        product_name=product_name,
                        cart_id=cart_id,
                    )
                    .first()
                )
                carts.quantity = quantity
                carts.final_price = final_price
                session.add(carts)
                session.commit()
                return False

    def get_total_price_product_or_all_carts_product(self, chat_id: int, order=False):
        """Возвращает стоимость всех заказов в корзине одного пользователя
        или список все товаров пользователя
        """
        with db_helper.get_session() as session:
            query = (
                select(self.model if order else func.sum(self.model.final_price))
                .join(Carts)
                .join(Users)
                .where(
                    Users.telegram == chat_id,
                )
            )

            finally_price = session.execute(query).fetchone()[0]
            list_carts = session.scalars(query).all()

            result = list_carts if order else finally_price

            return result
