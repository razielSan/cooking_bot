import asyncio

from expression import bot, dp
from views import router 


async def on_startup(bot):
    print("Бот запущенн")


async def on_shutdown(bot):
    print("бот лег")



async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
