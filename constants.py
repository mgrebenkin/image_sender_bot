from loguru import logger

from dotenv import load_dotenv,find_dotenv
from os import getenv
import json

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
if AUTH_ENABLED: 
    logger.info("Авторизация включена.")
else:
    logger.info("Авторизация отключена.")

try:
    USERNAME_WHITELIST = set(json.load(
        open('username_whitelist.json', 'r', encoding='utf-8')
    ))
except OSError:
    logger.exception("Ошибка чтения файла:", e)
    USERNAME_WHITELIST=set()
    
if (AUTH_ENABLED) and (len(USERNAME_WHITELIST) == 0):
    logger.warning("Список авторизаванных пользователей пуст!")