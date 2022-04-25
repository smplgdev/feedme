import asyncio
import json
from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaVideo, \
    InputMediaAudio, InputMediaAnimation
from aiogram_media_group import MediaGroupFilter, media_group_handler

from data.config import BOT_USERNAME
from filters.client_filter import ClientFilter
from filters.reply_filter import ReplyToMessageFilter
from loader import dp, bot
from utils.db_api.db_queries.channel import Channel


def get_message_text(initial_message: types.Message, message: dict, channel: dict, forward_data: dict) -> str:
    string = str()
    channel_title = channel['title']
    channel_id = channel['id']
    channel_username = channel['username']
    message_id = message['id']

    if channel['is_private']:
        private_hash = channel['private_hash']
        channel_link = f'<a href="https://t.me/c/{str(channel_id)[4:]}/{message_id}"><b>{channel_title}</b></a>'
    else:
        channel_link = f'<a href="https://t.me/{channel_username}/{message_id}"><b>{channel_title}</b></a>'


    string += channel_link + '\n'
    forward_from_string = None
    if message['is_forwarded']:
        peer_type = forward_data['peer']['peer_type']
        name = forward_data['peer']['name']
        username = forward_data['peer']['username'] or BOT_USERNAME
        if peer_type == 'PeerUser':
            forward_from_string = f'<a href="https://t.me/{username}">Пересланное сообщение от пользователя {name}</a>'
        elif peer_type == 'PeerChannel':
            forward_from_string = f'<a href="https://t.me/{username}">Пересланное сообщение из канала «{name}»</a>'
        elif peer_type == 'PeerChat':
            forward_from_string = f'<a href="https://t.me/{username}">Переслано из чата «{name}»</a>'

    if forward_from_string:
        string += forward_from_string + '\n\n'
    else:
        string += '\n'

    if initial_message.caption:
        msg_caption = initial_message.caption[:1023-len(string)]
        string += msg_caption
    elif initial_message.text:
        msg_text = initial_message.text[:4095-len(string)]
        string += msg_text

    return string


@dp.message_handler(MediaGroupFilter(), ClientFilter(), content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO,
                                                                       types.ContentType.DOCUMENT, types.ContentType.AUDIO])
@media_group_handler()
async def get_media_group_file_ids(messages: List[types.Message], state: FSMContext):
    files_list = list()
    for message in messages:
        if message.photo:
            files_list.append(['photo', message.photo[-1].file_id])
        elif message.video:
            files_list.append(['video', message.video.file_id])
        elif message.audio:
            files_list.append(['audio', message.audio.file_id])
        elif message.document:
            files_list.append(['document', message.document.file_id])
    await state.update_data({f"{messages[0].media_group_id}": files_list})

    # print(data.get(f"{messages[0].media_group_id}"))

@dp.message_handler(ClientFilter(), ReplyToMessageFilter(), content_types=types.ContentType.TEXT)
async def send_message_to_users(message: types.Message, state: FSMContext):
    json_msg = message.text
    msg = json.loads(json_msg)

    initial_message = message.reply_to_message
    message = msg['message']
    channel = msg['channel']
    forward_data = msg['forward_data']

    with_media = msg['with_media']
    is_album = msg['is_album']

    text = get_message_text(initial_message=initial_message,
                            message=message,
                            channel=channel,
                            forward_data=forward_data)

    channel_id = channel['id']
    users = await Channel(channel_id).get_followed_users()

    if not with_media:
        for user in users:
            await bot.send_message(chat_id=user.follower_telegram_id,
                                   text=text,
                                   disable_notification=True,
                                   disable_web_page_preview=True)
            await asyncio.sleep(1/20)
        return

    if initial_message.voice:
        for user in users:
            await bot.send_voice(user.follower_telegram_id,
                                 initial_message.voice.file_id,
                                 caption=text)
            await asyncio.sleep(1/20)
        return
    elif initial_message.video_note:
        for user in users:
            # await initial_message.forward(user.follower_telegram_id,
            #                               disable_notification=True)
            await bot.send_video_note(user.follower_telegram_id,
                                      initial_message.video_note.file_id)
            await asyncio.sleep(1/20)
        return
    elif initial_message.poll:
        for user in users:
            await initial_message.forward(user.follower_telegram_id,
                                          disable_notification=True)
            await asyncio.sleep(1/20)

    medias = list()
    if is_album:
        tries = 0
        while True:
            tries += 1
            await asyncio.sleep(3)
            data = await state.get_data()
            files = data.get(initial_message.media_group_id)
            await state.finish()
            if len(files) > 0:
                break
            if tries == 5:
                print('sending cancelled after 5 tries')
                return
        medias = list()
        for i, file in enumerate(files):
            caption = text if i == 1 else None
            if file[0] == 'photo':
                medias.append(InputMediaPhoto(file[1],
                                              caption=caption))
            elif file[0] == 'video':
                medias.append(InputMediaVideo(file[1],
                                              caption=caption))
            elif file[0] == 'audio':
                medias.append(InputMediaAudio(file[1],
                                              caption=caption))
            elif file[0] == 'document':
                medias.append(InputMediaDocument(file[1],
                                                 caption=caption))
    else:
        if initial_message.document:
            medias.append(InputMediaDocument(initial_message.document.file_id,
                                             caption=text))
        elif initial_message.photo:
            medias.append(InputMediaPhoto(initial_message.photo[-1].file_id,
                                          caption=text))
        elif initial_message.video:
            medias.append(InputMediaVideo(initial_message.video.file_id,
                                          caption=text))
        elif initial_message.audio:
            medias.append(InputMediaAudio(initial_message.audio.file_id,
                                          caption=text))
        elif initial_message.animation:
            medias.append(InputMediaAnimation(initial_message.animation.file_id,
                                              caption=text))
    if len(medias) > 0:
        for user in users:
            await bot.send_media_group(user.follower_telegram_id,
                                       medias,
                                       disable_notification=True)
            await asyncio.sleep(1/20)
        return
