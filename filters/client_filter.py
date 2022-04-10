from aiogram import types
from aiogram.dispatcher.filters import Filter

from data.config import CLIENTS_IDS


class ClientFilter(Filter):
    def __init__(self, is_client: bool = True):
        self.is_client = is_client

    async def check(self, message: types.Message):
        if self.is_client:
            return message.from_user.id in CLIENTS_IDS
        return message.from_user.id not in CLIENTS_IDS
