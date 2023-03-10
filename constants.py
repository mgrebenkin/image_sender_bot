from loguru import logger

from dotenv import load_dotenv,find_dotenv
from os import getenv
import json

load_dotenv(find_dotenv())

try:
    IMAGE_SENDER_BOT_API_TOKEN = getenv('IMAGE_SENDER_BOT_API_TOKEN', '')
    if (IMAGE_SENDER_BOT_API_TOKEN is None) or (IMAGE_SENDER_BOT_API_TOKEN == ''):
        raise Exception("Не удалось получить токен бота.")
    
    DB_PATH = getenv('DB_PATH', '')
    if (DB_PATH is None) or (DB_PATH == ''):
        raise Exception("Не указано расположение базы данных.")
except Exception as e:
    logger.exception("Ошибка переменной окружения: ", e)
    exit()

AUTH_ENABLED = getenv('ENABLE_AUTH', 'False').lower() in ['true', 't', '1', 'yes', 'y']
if AUTH_ENABLED: 
    logger.info("Авторизация включена.")
else:
    logger.info("Авторизация отключена.")

try:
    USERNAME_WHITELIST = set(json.load(
        open('username_whitelist.json', 'r', encoding='utf-8')
    ))
    """List of authorized usernames"""
except OSError as e:
    logger.exception("Ошибка чтения файла:", e)
    USERNAME_WHITELIST=set()

if (AUTH_ENABLED) and (len(USERNAME_WHITELIST) == 0):
    logger.warning("Список авторизованных пользователей пуст!")

TASK_LOOP_PERIOD = 0.5
"""Time of sleep between aioschedule checks"""

DAILY_SENDING_TIME = '15:00'
"""Time of day to do daily sending"""