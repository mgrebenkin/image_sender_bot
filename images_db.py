from loguru import logger
import sqlite3
import exceptions
import io
import random

class ImagesDB:
    def __init__(self, path: str) -> None:
            self.connection: sqlite3.Connection = sqlite3.connect(path)
            try:
                self.image_count: int = self.query_image_count()
            except exceptions.CantCountImages:
                logger.exception(
                    """Не удалось посчитать количество изображений при подулючении БД.""")
            else:
                logger.info(
                    f"""База инициализирована. Найдено {self.image_count} изображений.""")

    def query_image_count(self) -> int:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """SELECT COUNT(IMG_BLOBS)
                FROM IMAGES""")
            self.connection.commit()
        except sqlite3.Error as e:
            logger.exception('Ошибка базы данных:', e)
            raise exceptions.CantCountImages 
        self.image_count = cursor.fetchone()[0]
        cursor.close()   
        return self.image_count
    
    def fetch_random_image(self) -> io.BytesIO:
        if self.image_count == 0: 
             raise exceptions.NoImages
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """SELECT IMG_BLOBS
                FROM IMAGES
                LIMIT 1 OFFSET :offset""",
                {'offset': random.randint(0, self.image_count - 1)}
                )
            self.connection.commit()
        except sqlite3.Error as e:
             logger.exception("Ошибка базы данных:", e)
             raise exceptions.CantFetchImage
        bitmap = cursor.fetchone()[0]
        cursor.close()
        return io.BytesIO(bitmap)
    
    def store_image(self, img_blob: io.BytesIO) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """INSERT INTO IMAGES(IMG_BLOBS)
                VALUES (:img_blob)""",
                {'img_blob': sqlite3.Binary(img_blob.read())}
            )
            self.connection.commit()
        except sqlite3.Error as e:
             logger.exception("Ошибка базы данных", e)
             raise exceptions.CantStoreImage
        else:
             self.image_count+=1
        cursor.close()
        
