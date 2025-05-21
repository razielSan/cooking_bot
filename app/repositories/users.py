from sqlalchemy import update

from database import Users
from database.db_helper import db_helper


class UsersSQLAlchemyRepository:
    model = Users

    def register_user(self, name: str, telegram: int) -> bool:
        """Первая регистрация пользователя с доступными данными"""
        with db_helper.get_session() as sessiion:
            try:
                query = self.model(
                    name=name,
                    telegram=telegram,
                )
                sessiion.add(query)
                sessiion.commit()
                return True
            except Exception as err:
                print(err)
                sessiion.rollback()
                return False

    def add_phone_user(self, telegram: int, phone: str):
        """Дополняем данные пользователя телефонным номером"""
        with db_helper.get_session() as session:
            # Один из способов запроса

            # query = (
            #     update(self.model)
            #     .where(self.model.telegram == telegram)
            #     .values(
            #         phone=phone,
            #     )
            # )

            session.query(self.model).filter(self.model.telegram == telegram).update(
                {self.model.phone: phone}
            )

            session.commit()
