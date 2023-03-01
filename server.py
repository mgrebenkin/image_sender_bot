from loguru import logger

from constants import IMAGE_SENDER_BOT_API_TOKEN, AUTH_ENABLED, DB_PATH
from aiogram import Bot, Dispatcher, executor, types
from images_db import ImagesDB
import exceptions
import io

logger.add('log/log.log', retention=1)

try:
    bot = Bot(token = IMAGE_SENDER_BOT_API_TOKEN)
    dp = Dispatcher(bot=bot)
except Exception as e:
    logger.exception("Ошибка инициализации бота:", e)
else:
    logger.info("Бот инициализирован.")

img_db = ImagesDB(DB_PATH)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def store_image(message: types.Message):
    img_blob = io.BytesIO()
    await message.photo[-1].download(destination_file=img_blob)
    try:
        img_db.store_image(img_blob=img_blob)
    except exceptions.CantStoreImage:
        await message.answer("Не удалось сохранить изображение")

@dp.message_handler(commands=['send'])
async def send_random_image(message: types.Message):
    try:
        fetched_image = types.InputFile(img_db.fetch_random_image())
    except exceptions.CantFetchImage as e:
        await message.answer(text="Не удалось получить изображение.")
    else:
        await message.answer_photo(photo=fetched_image)

if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=None)
    except Exception as e:
        logger.exception("Не удалось авторизовать бота: ", e)
        