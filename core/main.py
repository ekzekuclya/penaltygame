import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

import asyncio
import logging

BOT_TOKEN = '6935064173:AAHQJ4Wma-FSEAU90uoFbsPZqWZEA37Sac4'

async def main():
    from aiogram.enums.parse_mode import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram import Bot, Dispatcher
    from penalty_app.handlers import start, gamestart, maingame

    bot = Bot(token=BOT_TOKEN, parse_mode=None)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start.router, gamestart.router, maingame.router)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())