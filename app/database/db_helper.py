from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings


class DataBaseHelper:
    def __init__(self):
        self.engine = create_engine(url=settings.get_url_postgres)
        self.session_factory = sessionmaker(bind=self.engine)

    def get_session(self):
        with self.session_factory() as session:
            return session


db_helper = DataBaseHelper()
