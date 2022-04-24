from aiogram import types
from aiogram.dispatcher.filters import Filter


class ReplyToMessageFilter(Filter):

    async def check(self, message: types.Message):
        return message.reply_to_message

