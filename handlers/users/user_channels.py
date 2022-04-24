from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from handlers.users.start import user_channels_text, how_to_subscribe_text
from loader import dp
from utils.db_api import quick_commands as qc
from utils.db_api.db_queries.channel import Channel
from utils.db_api.db_queries.follower import Follower

select_channel_callback_data = CallbackData("select_channel", "channel_id")
delete_channel_callback = CallbackData("unfollow_channel", "channel_id", "decision")

def get_user_channels_markup(channels: list):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=channel.title, callback_data=select_channel_callback_data.new(
                channel_id=channel.channel_id
            ))
        ] for channel in channels
    ])
    return markup


def get_unfollow_confirmation(channel_id: int, channel_link: str = None, private_hash: str = None):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🗑 Отписаться', callback_data=delete_channel_callback.new(
                channel_id=channel_id,
                decision="unfollow"
            )),
            InlineKeyboardButton(text='Перейти на канал', url=f'https://t.me/{channel_link or "+" + private_hash}'),
        ],
        [
            InlineKeyboardButton(text='Вернуться назад', callback_data=delete_channel_callback.new(
                channel_id=channel_id,
                decision="cancel"
            ))
        ]
    ])
    return markup


@dp.message_handler(Command("channels"))
@dp.message_handler(text=user_channels_text)
async def list_user_channels(message: types.Message, user_telegram_id = None):
    user_telegram_id = user_telegram_id or message.from_user.id
    user_channels = await Follower(user_telegram_id).get_following_channels()
    if len(user_channels) == 0:
        await message.answer("Вы не подписаны ни на один канал!")
        await message.answer(how_to_subscribe_text)
        return
    channels_markup = get_user_channels_markup(user_channels)
    await message.answer("Список ваших каналов находится ниже. Чтобы отписаться, нажмите по кнопке канала",
                         reply_markup=channels_markup)


@dp.callback_query_handler(select_channel_callback_data.filter())
async def unsubscribe_from_channel(call: types.CallbackQuery, callback_data: dict):
    channel_id = int(callback_data.get("channel_id"))
    channel = await Channel(channel_id).get()
    await call.message.edit_text("Вы находитесь в меню настроек канала «<b>%s</b>»" % channel.title,
                                 reply_markup=get_unfollow_confirmation(channel_id, channel.invite_link))


@dp.callback_query_handler(delete_channel_callback.filter(decision='unfollow'))
async def unfollow_from_channel_handler(call: types.CallbackQuery, callback_data: dict):
    channel_id = int(callback_data.get("channel_id"))
    follower_id = call.from_user.id
    await Follower(follower_id).delete_follower(channel_id)
    await call.message.delete()
    await call.answer("Вы успешно отписались от этого канала.", show_alert=True)
    await list_user_channels(call.message, call.from_user.id)


@dp.callback_query_handler(delete_channel_callback.filter(decision='cancel'))
async def cancel_unfollow_handler(call: types.CallbackQuery):
    await call.message.delete()
    await list_user_channels(call.message, call.from_user.id)
