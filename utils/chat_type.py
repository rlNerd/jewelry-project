from aiogram.filters import Filter
from aiogram import Bot, types

from database import request as rq


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]):
        self.chat_types = chat_types

    async def __call__(self, message: types.Message):
        return message.chat.type in self.chat_types


class IsAdmin(Filter):
    def __init__(self):
        pass

    async def __call__(self, message: types.Message, bot: Bot):
        check_tg_status = await rq.check_adm_status(message.from_user.id)
        return check_tg_status.status