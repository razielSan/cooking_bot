from aiogram import Bot, Dispatcher

from config.settings import settings

dp = Dispatcher()
bot = Bot(token=settings.TOKEN)
