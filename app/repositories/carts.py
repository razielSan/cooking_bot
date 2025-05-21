from sqlalchemy import select

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
                user = session.query(Users).filter_by(
                    telegram=chat_id,
                ).first()
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
