import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import TOKEN
from .handlers import register_handlers

from .db import init_db
async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    init_db()
    register_handlers(dp)

    print("aiogram бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

