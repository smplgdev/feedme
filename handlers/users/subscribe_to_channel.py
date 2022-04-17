import json
from typing import List

from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram_media_group import MediaGroupFilter, media_group_handler

from filters.client_filter import ClientFilter
from loader import dp, bot
from utils.db_api.db_queries.channel import Channel


@dp.message_handler(MediaGroupFilter(), ClientFilter(False), content_types=[types.ContentType.PHOTO,
                                                                            types.ContentType.VIDEO,
                                                                            types.ContentType.DOCUMENT,
                                                                            types.ContentType.AUDIO],
                    is_forwarded=True)
@media_group_handler()
async def media_subscribe_handler(messages: List[types.Message]):
    message = messages[0]
    await subscribe_to_channel(message)


@dp.message_handler(ClientFilter(False), regexp=r'@(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*')
@dp.message_handler(ClientFilter(False), ChatTypeFilter([types.ChatType.PRIVATE]),
                    is_forwarded=True, content_types=types.ContentType.ANY)
@dp.message_handler(ClientFilter(False), regexp=r'(https?:\/\/)?(www[.])?(telegram|t)\.me\/')
async def subscribe_to_channel(message: types.Message):
    channel_hash = None
    channel_id = None
    channel_title = None
    channel_username = None
    if message.forward_from_chat:
        # If forwarded message was provided
        channel_id = message.forward_from_chat.id
        channel_username = message.forward_from_chat.username
        channel_invite_link = message.forward_from_chat.username
        channel_title = message.forward_from_chat.full_name
    elif message.text.startswith("@"):
        # If @username was provided
        channel_username = message.text[1:]
        channel_invite_link = channel_username
    else:
        # If link was provided
        channel_invite_link = message.text.split("t.me/")[-1]
        if "/+" in message.text:
            # For private channels
            channel_hash = message.text.split("/+")[-1]
            channel_invite_link = None

    client_data = await Channel(channel_id).select_client(channel_username, channel_invite_link, channel_hash)
    message_dict = {
        "from_user_id": message.from_user.id,
        "is_forward": message.is_forward(),
        "message_id": message.message_id,
    }
    channel = {
        "id": channel_id,
        "username": channel_username,
        "title": channel_title,
        "invite_link": channel_invite_link,
        "private_hash": channel_hash,
    }
    client = {
        "id": client_data.telegram_id,
        "is_running": client_data.is_running
    }

    to_json = {"message": message_dict, "channel": channel, "client": client}
    json_message = json.dumps(to_json)
    await bot.send_message(client_data.telegram_id, json_message)
