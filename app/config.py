import os
from dotenv import load_dotenv

# Загружаем переменные среды, если есть .env файл
load_dotenv(dotenv_path=".env")


class Settings:
    # Настройки авторизации AMOCRM
    DATABASE_URL: str = "sqlite:///./elements_timeline.db"
    AMOCRM_USERNAME: str = os.getenv("AMOCRM_USERNAME", "")
    AMOCRM_PASSWORD: str = os.getenv("AMOCRM_PASSWORD", "")
    AMOCRM_SUBDOMAIN: str = os.getenv("AMOCRM_SUBDOMAIN", "")

    AMOCRM_CLIENT_ID: str = os.getenv("AMOCRM_CLIENT_ID", "")
    AMOCRM_CLIENT_SECRET: str = os.getenv("AMOCRM_CLIENT_SECRET", "")
    AMOCRM_REDIRECT_URI: str = os.getenv("AMOCRM_REDIRECT_URI", "")

    # Проверка на обязательные переменные

    @staticmethod
    def validate():
        missing_vars = []
        if not Settings.AMOCRM_USERNAME:
            missing_vars.append("AMOCRM_USERNAME")
        if not Settings.AMOCRM_PASSWORD:
            missing_vars.append("AMOCRM_PASSWORD")
        if not Settings.AMOCRM_SUBDOMAIN:
            missing_vars.append("AMOCRM_SUBDOMAIN")
        if not Settings.DATABASE_URL:
            missing_vars.append("DATABASE_URL")

        if missing_vars:
            raise EnvironmentError(
                f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")


# Выполнить проверку при инициализации
Settings.validate()

SETTINGS = Settings()


# Список менеджеров и их имён
TARGET_CONTACTS = {
    "8985106": "Владислав Екимов",
    "8513983": "Логачев Дмитрий",
    "11275370": "Шамраев Владимир",
    "11638242": "Регентов Михаил",
    "10878426": "Кузьмин Сергей",
    "11089494": "Борисов Максим",
    "11667306": "Мегель Константин",
    "9024302": "Непочатов Виталий",
    "9932914": "Петров Александр",
    "8421595": "Чеботарев Андрей"
}


PIPELINE = {
    "3506236": "AnyQuery (SMB/SME)",
}

STATUSES = {
    "34649026": "Интро демо запланировано",
}
