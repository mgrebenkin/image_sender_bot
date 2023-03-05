from loguru import logger

from constants import IMAGE_SENDER_BOT_API_TOKEN, AUTH_ENABLED, DB_PATH, USERNAME_WHITELIST
from aiogram import Bot, Dispatcher, executor, types
from images_db import ImagesDB
import exceptions
import io
import aioschedule
from asyncio import sleep as aiosleep


logger.add('log/log.log', retention=1)

try:
    bot = Bot(token = IMAGE_SENDER_BOT_API_TOKEN)
    dp = Dispatcher(bot=bot)
except Exception as e:
    logger.exception("Ошибка инициализации бота:", e)
else:
    logger.info("Бот инициализирован.")

img_db = ImagesDB(DB_PATH)

def auth(func):

    async def wrapper(message: types.Message):
        if not (message.from_user.username in USERNAME_WHITELIST) and (AUTH_ENABLED):
            return await message.reply("Нет доступа")
        return await func(message)
    
    return wrapper


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
@auth
async def store_image(message: types.Message):
    img_blob = io.BytesIO()
    await message.photo[-1].download(destination_file=img_blob)
    try:
        img_db.store_image(img_blob=img_blob)
        await message.answer("Изображение сохранено.")
    except exceptions.CantStoreImage:
        await message.answer("Не удалось сохранить изображение.")


@dp.message_handler(commands=['send'])
@auth
async def answer_with_random_image(message: types.Message):
    try:
        fetched_image = types.InputFile(img_db.fetch_random_image())
    except exceptions.CantFetchImage as e:
        await message.answer(text="Не удалось получить изображение.")
    else:
        await message.answer_photo(photo=fetched_image)

async def send_random_image(user_id: int ):
    try:
        fetched_image = types.InputFile(img_db.fetch_random_image())
    except exceptions.CantFetchImage as e:
        await bot.send_message(chat_id=user_id, text="Не удалось получить изображение.")
    else:
        await bot.send_photo(chat_id=user_id, photo=fetched_image)

async def test(user_id: int):
    await bot.send_message(chat_id=user_id, text="test")

async def startup_routine(_):
    aioschedule.every().day.at('15:00').do(send_random_image, user_id=None)
    while True:
        await aioschedule.run_pending()
        await aiosleep(0.5)
        

if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup_routine)
    except Exception as e:
        logger.exception("Не удалось авторизовать бота: ", e)
        