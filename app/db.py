from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from app.config import SETTINGS

Base = declarative_base()

# Подключение к SQLite (считывается из SETTINGS)
engine = create_engine(SETTINGS.DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Инициализация базы данных (создание таблиц).
    """
    CustomBase.metadata.create_all(bind=engine)


@as_declarative()
class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self):
        """
        Рекурсивно преобразует SQLAlchemy объект в словарь.
        """
        def serialize(value):
            if isinstance(value, datetime.datetime):
                # Конвертация объекта datetime в ISO формат
                return value.isoformat()
            elif isinstance(value, list):
                # Рекурсивно обрабатываем списки
                return [serialize(i) for i in value]
            elif hasattr(value, "__dict__"):  # SQLAlchemy объект
                return {k: serialize(v) for k, v in value.__dict__.items() if not k.startswith("_")}
            return value

        return serialize(self)
