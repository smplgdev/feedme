from aiogram import types
from aiogram.dispatcher.filters import Command

from data.config import ADMINS
from loader import dp
from utils.db_api.db_queries.channel import Channel
from utils.functions.update_channels_info import update_channels


@dp.message_handler(Command("update_channels"), user_id=ADMINS)
async def update_channels_handler(message: types.Message):
    dublicates = await Channel.get_dublicated_channels()
    await message.answer("Дублированные каналы:\n\n{}"
                         .format("\n".join(f"{channel[0]} — {channel[2]} — {channel[1]}" for channel in dublicates)))
