import os

import dotenv
from aiogram import Bot

dotenv.load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
