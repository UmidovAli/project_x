import asyncio
import logging
import os

import dotenv
from aiogram import Dispatcher

from data import database

from config import bot
from handlers import get_full_router

dotenv.load_dotenv()
bot = bot
dp = Dispatcher()
logger = logging.getLogger(__name__)

dev = 'xeeliq'


async def main():
    await database.init_db()
    logging.basicConfig(level=logging.DEBUG)
    dp.include_router(get_full_router())

    await dp.start_polling(bot)
    await bot.get_my_description()


if __name__ == '__main__':
    asyncio.run(main())
