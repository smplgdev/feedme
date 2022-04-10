import asyncio
import json
from typing import List

from aiogram import types
from aiogram_media_group import MediaGroupFilter, media_group_handler

from data.config import BOT_USERNAME
from filters.client_filter import ClientFilter
from loader import dp, bot
from utils.db_api import quick_commands as qc
from utils.db_api.db_queries.channel import Channel
from utils.db_api.schemas.forwarded_messages import ForwardMessage


def get_forwarded_message_caption_text(replied_message: types.Message,
                                       forwarded_message_data: ForwardMessage,
                                       message_id_follower_chat: int,
                                       is_message_type_text=False,
                                       ):
    message_caption = replied_message.parse_entities()
    caption = f"<b><a href='https://t.me/{forwarded_message_data.who_forwarded_chat_username or BOT_USERNAME}/{message_id_follower_chat}'>" \
              f"{str(forwarded_message_data.who_forwarded_chat_title)}</a></b>\n" \
              f"<a href='https://t.me/{forwarded_message_data.chat_username}/{forwarded_message_data.message_id}'>" \
              f"Пересланное сообщение из канала <b>«{forwarded_message_data.chat_title}»</b></a>\n\n" + message_caption
              # f"<a href='https://t.me/{forwarded_message_data.chat_username}/{forwarded_message_data.message_id}'>" \
    if is_message_type_text:
        return caption[:4095]
    return caption[:1023]


@dp.message_handler(MediaGroupFilter(), ClientFilter(), content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO,
                                                                       types.ContentType.DOCUMENT, types.ContentType.AUDIO],
                    is_forwarded=False)
@media_group_handler()
async def answer_media_group(messages: List[types.Message]):
    pass


@dp.message_handler(ClientFilter(), is_forwarded=False, content_types=types.ContentType.TEXT,
                    regexp=r'^{"forward_data":')
async def forward_forwarded_message(message: types.Message):
    json_msg = json.loads(message.text)
    messages = json_msg['messages']
    forwarded_data = await qc.get_forwarded_message_query(messages[0]['id']) # ПОДПИСЧИКИ КАНАЛА
    message = message.reply_to_message # КАНАЛ, ОТКУДА ПЕРЕСЫЛАЕМ [ПЕРЕСЛАНО ИЗ КАНАЛА ...]

    channel_id = forwarded_data.who_forwarded_chat_id
    users = await Channel(channel_id).get_followed_users()
    message_type = message.content_type
    message_id_follower_chat = messages[0]['message_id']

    disable_web_preview = True
    if message_type == 'text':
        caption = get_forwarded_message_caption_text(message, forwarded_data, message_id_follower_chat, is_message_type_text=True)
        for user in users:
            await bot.send_message(user.follower_telegram_id, caption,
                                   disable_web_page_preview=disable_web_preview)
            await asyncio.sleep(0.35)
    elif message_type == 'photo':
        caption = get_forwarded_message_caption_text(message, forwarded_data, message_id_follower_chat)
        for user in users:
            await bot.send_photo(user.follower_telegram_id, message.photo[-1].file_id, caption=caption)
            await asyncio.sleep(0.35)
    elif message_type == 'video':
        caption = get_forwarded_message_caption_text(message, forwarded_data, message_id_follower_chat)
        for user in users:
            await bot.send_video(user.follower_telegram_id, message.video.file_id, caption=caption)
            await asyncio.sleep(0.35)
    elif message_type == 'document':
        caption = get_forwarded_message_caption_text(message, forwarded_data, message_id_follower_chat)
        for user in users:
            await bot.send_document(user.follower_telegram_id, message.document.file_id, caption=caption)
            await asyncio.sleep(0.35)
    elif message_type == 'voice':
        caption = get_forwarded_message_caption_text(message, forwarded_data, message_id_follower_chat)
        for user in users:
            await bot.send_voice(user.follower_telegram_id, message.voice.file_id, caption=caption)
            await asyncio.sleep(0.35)
    else:
        pass
        # caption = get_forwarded_message_caption_text(msg, message)
        # for user in users:
        #     await bot.send_file(user.follower_telegram_id, message_type, message.message_type.file_id, caption)
        #     await asyncio.sleep(0.35)