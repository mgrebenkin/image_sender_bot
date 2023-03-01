from loguru import logger

from dotenv import load_dotenv,find_dotenv
from os import getenv

load_dotenv(find_dotenv())

try:
    IMAGE_SENDER_BOT_API_TOKEN = getenv('IMAGE_SENDER_BOT_API_TOKEN')
    if IMAGE_SENDER_BOT_API_TOKEN is None:
        raise Exception("Не удалось получить токен бота.")
    
    DB_PATH = getenv('DB_PATH')
    if DB_PATH is None:
        raise Exception("Не указано расположение базы данных.")
except Exception as e:
    logger.warning("Ошибка переменной окружения: ", e)

AUTH_ENABLED = getenv('ENABLE_AUTH', 'False').lower() in ['true', 't', '1', 'yes', 'y']
