import asyncio
from typing import List

from aiogram import types
from aiogram.types import InputMediaPhoto, MediaGroup, InputMediaDocument, InputMediaVideo, \
    InputMediaAudio
from aiogram.utils.exceptions import BotBlocked
from aiogram_media_group import MediaGroupFilter, media_group_handler

from data.config import BOT_USERNAME
from filters.client_filter import ClientFilter
from loader import dp, bot
from utils.db_api.db_queries.channel import Channel
from utils.db_api.db_queries.follower import Follower
from utils.db_api.db_queries.telegram_user import TelegramUser


def get_caption_text(message: types.Message, is_message_type_text=False):
    message_caption = str()
    try:
        message_caption = message.parse_entities()
    except TypeError:
        # Not text message
        pass
    caption = f"<b><a href='https://t.me/{message.forward_from_chat.username or BOT_USERNAME}/{message.forward_from_message_id}'>" \
              f"{str(message.forward_from_chat.title)}</a></b>\n\n" + message_caption
    if is_message_type_text:
        return caption[:4095]
    return caption[:1023]


@dp.message_handler(MediaGroupFilter(), ClientFilter(), content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO,
                                                                       types.ContentType.DOCUMENT, types.ContentType.AUDIO],
                    is_forwarded=True)
@media_group_handler()
async def answer_media_group(messages: List[types.Message]):
    channel_id = messages[0].forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()
    media = MediaGroup()
    message_ = messages[0]

    caption = get_caption_text(message_)

    for i in range(len(messages)):
        if messages[i].photo:
            media.attach(InputMediaPhoto(messages[i].photo[-1].file_id, caption=caption if i == 0 else None))
        elif messages[i].document:
            media.attach(InputMediaDocument(messages[i].document.file_id, caption=caption if i == 0 else None))
        elif messages[i].video:
            media.attach(InputMediaVideo(messages[i].video.file_id, caption=caption if i == 0 else None))
        elif messages[i].audio:
            media.attach(InputMediaAudio(messages[i].audio.file_id, caption=caption if i == 0 else None))

    for user in users:
        try:
            await bot.send_media_group(user.follower_telegram_id, media)
        except BotBlocked:
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=types.ContentType.TEXT)
async def send_text_handler(message: types.Message):
    text = get_caption_text(message, is_message_type_text=True)
    channel_id = message.forward_from_chat.id
    if channel_id == -1001763044206:
        # FEEDTG
        users = await TelegramUser.get_all_users()
        for user in users:
            try:
                await bot.send_message(user.telegram_id, text, disable_web_page_preview=True)
            except BotBlocked:
                follower = Follower(user.follower_telegram_id)
                await follower.delete_follower(channel_id)
                await follower.make_inactive()
                pass
            await asyncio.sleep(0.35)
        return
    users =  await Channel(channel_id).get_followed_users()

    # disable_web_preview = not('<a href' in message.parse_entities())
    disable_web_preview = True
    # if len(text) > 1000:
    #     shortened_text = text[:400] + "..."
    #     markup = get_show_full_markup(await qc.create_shortened_message(text))
    #     for user in users:
    #         await bot.send_message(user.follower_telegram_id,
    #                                shortened_text,
    #                                reply_markup=markup,
    #                                disable_web_page_preview=disable_web_preview)
    #         await asyncio.sleep(0.35)
    #     return

    for user in users:
        try:
            await bot.send_message(user.follower_telegram_id, text,
                                   disable_web_page_preview=disable_web_preview)
        except BotBlocked:
            # TODO: rm from db
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=types.ContentType.POLL)
async def send_poll(message: types.Message):
    channel_id = message.forward_from_chat.id
    users =  await Channel(channel_id).get_followed_users()
    for user in users:
        try:
            await message.forward(user.follower_telegram_id)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.PHOTO])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users =  await Channel(channel_id).get_followed_users()
    caption = get_caption_text(message)

    for user in users:
        try:
            await bot.send_photo(user.follower_telegram_id, message.photo[-1].file_id, caption)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.VIDEO])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()
    caption = get_caption_text(message)

    for user in users:
        try:
            await bot.send_video(user.follower_telegram_id, message.video.file_id, caption=caption)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.DOCUMENT])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()
    caption = get_caption_text(message)
    for user in users:
        try:
            await bot.send_document(user.follower_telegram_id, message.document.file_id, caption=caption)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.AUDIO])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()
    caption = get_caption_text(message)

    for user in users:
        try:
            await bot.send_audio(user.follower_telegram_id, message.audio.file_id, caption=caption)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.VOICE])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()
    caption = get_caption_text(message)

    for user in users:
        try:
            await bot.send_voice(user.follower_telegram_id, message.voice.file_id, caption=caption)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.ANIMATION])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()
    caption = get_caption_text(message)

    for user in users:
        try:
            await bot.send_animation(user.follower_telegram_id, message.animation.file_id, caption=caption)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)


@dp.message_handler(ClientFilter(), is_forwarded=True, content_types=[types.ContentType.STICKER])
async def forward_photo_handler(message: types.Message):
    channel_id = message.forward_from_chat.id
    users = await Channel(channel_id).get_followed_users()

    for user in users:
        try:
            await bot.send_sticker(user.follower_telegram_id, message.sticker.file_id)
        except BotBlocked:
            follower = Follower(user.follower_telegram_id)
            await follower.delete_follower(channel_id)
            await follower.make_inactive()
            pass
        await asyncio.sleep(0.35)
