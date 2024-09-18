import asyncio
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommandScopeAllPrivateChats


from database.models import async_main
from handlers.user import user_router
from handlers.admin_panel import admin_router
from utils.command_menu import cmd_menu_list


async def main():
    await async_main()
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(user_router, admin_router)
    await bot.set_my_commands(commands=cmd_menu_list, scope=BotCommandScopeAllPrivateChats())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print('Start')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')