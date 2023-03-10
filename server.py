from loguru import logger

from constants import IMAGE_SENDER_BOT_API_TOKEN, AUTH_ENABLED, \
    DB_PATH, USERNAME_WHITELIST, TASK_LOOP_PERIOD, DAILY_SENDING_TIME
from aiogram import Bot, Dispatcher, executor, types
from images_db import ImagesDB
import exceptions
import io
import aioschedule
import asyncio


logger.add('log/log.log', retention=1)

try:
    bot = Bot(token = IMAGE_SENDER_BOT_API_TOKEN)
    dp = Dispatcher(bot=bot)
except Exception as e:
    logger.exception("Ошибка инициализации бота:", e)
    exit()
else:
    logger.info("Бот инициализирован.")

img_db = ImagesDB(DB_PATH)

async def do_daily_sending():
    """Starts a loop that checks for aioschedule jobs to do"""
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(TASK_LOOP_PERIOD)

def auth(func):
    """Decorator to authorize user"""
    async def wrapper(message: types.Message):
        if not (message.from_user.username in USERNAME_WHITELIST) and (AUTH_ENABLED):
            logger.info(f"Отказано в доступе пользователю {message.from_user.username}.")
            return await message.reply("Нет доступа")
        return await func(message)
    
    return wrapper


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
@auth
async def store_image(message: types.Message):
    """Saves image sent by user to database"""
    img_blob = io.BytesIO()
    await message.photo[-1].download(destination_file=img_blob)
    try:
        img_db.store_image(img_blob=img_blob)
        await message.answer("Изображение сохранено.")
        logger.info(f"Изображение от пользователя {message.from_user.username} сохранено.")
    except exceptions.CantStoreImage as e:
        logger.exception(f"Не удалось сохранить изображение от пользователя {message.from_user.username}", e)
        await message.answer("Не удалось сохранить изображение.")


@dp.message_handler(commands=['send'])
@auth
async def answer_with_random_image(message: types.Message):
    """Answers to user with random image from database"""
    try:
        fetched_image = types.InputFile(img_db.fetch_random_image())
    except exceptions.CantFetchImage as e:
        logger.exception(f"Не удалось ответить пользователю {message.from_user.username}:", e)
        await message.answer(text="Не удалось получить изображение.")
    else:
        await message.answer_photo(photo=fetched_image)
        logger.info(f"Бот ответил пользователю {message.from_user.username}.")

async def send_random_image(user_id: int ):
    """Sends random image to user with user_id"""
    try:
        fetched_image = types.InputFile(img_db.fetch_random_image())
    except exceptions.CantFetchImage as e:
        logger.exception(f"Не удалось отправить изображение пользователю с id {user_id}", e)
        await bot.send_message(chat_id=user_id, text="Не удалось получить изображение.")
    else:
        await bot.send_photo(chat_id=user_id, photo=fetched_image)
        logger.info(f"Отправлено изображение пользователю с id {user_id}")

async def test(user_id: int):
    """Sends "test" to user with user_id"""
    await bot.send_message(chat_id=user_id, text="test")

async def startup_routine(_):
    """Schedules daily sending jobs and starts checking loop"""
    aioschedule.every().day.at(DAILY_SENDING_TIME).do(send_random_image, user_id=None)
    logger.info(f"Запланирована отправка изображения пользователю с id {None}")
    asyncio.create_task(do_daily_sending())
        

if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup_routine)
    except Exception as e:
        logger.exception("Не удалось авторизовать бота: ", e)
        