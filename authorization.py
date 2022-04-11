import asyncio
import json
import logging

from telethon import TelegramClient, events
from telethon.errors import ChannelPrivateError, MessageIdInvalidError
from telethon.tl import functions
from telethon.tl.types import PeerChannel, InputMessageID

from data.config import BOT_ID, POSTGRES_URI, ADMINS
from handlers.clients.follow_status import success_text
from utils.db_api import quick_commands as qc
from utils.db_api.db_gino import db
from utils.db_api.db_queries.client import Client
from utils.db_api.db_queries.follower import Follower
from utils.functions.clients.add_follow import get_following_status
from utils.functions.clients.json_messages import deserialize_bot_json, serialize_message_to_bot


async def run_client(client):
    async with await client.start():
        @client.on(events.NewMessage(chats=BOT_ID, incoming=True))
        async def send_message_to_bot(event):
            channel, follower_id, is_following, message_id = await deserialize_bot_json(client, event.message.text)
            status = await get_following_status(follower_id, channel, is_following)
            if status == success_text:
                await Follower(follower_id).add_follower(channel.telegram_id)
            message_text = await serialize_message_to_bot(follower_id=follower_id,
                                                          channel=channel,
                                                          message_id=message_id,
                                                          status=status)
            await client.send_message(BOT_ID, message_text)


        @client.on(events.Album())
        async def forward_album(event):
            message = event.messages[0]
            is_forwarded = message.fwd_from
            if is_forwarded:
                fwd_info = None
                chat_id = 0
                if isinstance(is_forwarded.from_id, PeerChannel):
                    try:
                        fwd_info = await client(functions.channels.GetFullChannelRequest(message.fwd_from.from_id))
                        chat_id = message.fwd_from.from_id.channel_id
                    except ChannelPrivateError as e:
                        logging.info(e)
                        pass
                # elif isinstance(is_forwarded.from_id, PeerUser):
                #     fwd_info = await client(functions.users.GetFullUserRequest(message.fwd_from.from_id))
                # elif isinstance(is_forwarded.from_id, PeerChat):
                #     fwd_info = await client(functions.messages.GetFullChatRequest(message.fwd_from.from_id))

                channel_title = fwd_info.chats[0].title
                channel_username = fwd_info.chats[0].username

                messages_list = list()
                to_json = dict(
                    forward_data=dict(
                        chat_id=chat_id,
                        chat_title=int("-100" + str(chat_id)),
                        chat_username=channel_username,
                        who_forwarded_chat_id=int("-100" + str(message.chat.id)),
                        who_forwarded_chat_title=message.chat.title,
                        who_forwarded_chat_username=message.chat.username
                    ),
                    messages=messages_list
                )
                for msg in event.messages:
                    message_data=await qc.create_forwarded_message(message_id=msg.fwd_from.channel_post,
                                                                   chat_id=int("-100" + str(chat_id)),
                                                                   chat_title=channel_title,
                                                                   chat_username=channel_username,
                                                                   who_forwarded_chat_id=int("-100" + str(message.chat.id)),
                                                                   who_forwarded_chat_title=message.chat.title,
                                                                   who_forwarded_chat_username=message.chat.username)
                    messages_list.append(dict(
                        id=message_data.id,
                        message_id=msg.id,
                    ))
                json_msg = json.dumps(to_json)
                msg = await client.send_message(
                    BOT_ID,
                    file=event.messages,
                    message=list(map(lambda a: str(a.message), event.messages))
                )
                await client.send_message(BOT_ID, json_msg, reply_to=msg[0])
                return
            try:
                await event.forward_to(BOT_ID)
            except MessageIdInvalidError as e:
                logging.info(e)

        @client.on(events.NewMessage(forwards=True))
        async def send_forwarded_message(event):
            message = event.message

            if event.media:
                channel_messages = await client(functions.channels.GetMessagesRequest(
                    channel=event.message.chat,
                    id=[InputMessageID(event.message.id - 1), InputMessageID(event.message.id + 1)]
                ))

                previous_message = channel_messages.messages[0]
                next_message = channel_messages.messages[1]
                if (previous_message.date == event.message.date or next_message.date == event.message.date) \
                        and (previous_message.media or next_message.media):
                    return
            try:
                channel_id = message.fwd_from.from_id.channel_id
            except AttributeError:
                return
            try:
                channel_info = await client(functions.channels.GetFullChannelRequest(channel_id))
            except ValueError:
                return
            except ChannelPrivateError:
                return
            channel_title = channel_info.chats[0].title
            channel_username = channel_info.chats[0].username
            messages_list = list()
            to_json = dict(
                forward_data=dict(
                    chat_id=channel_id,
                    chat_title=int("-100" + str(channel_id)),
                    chat_username=channel_username,
                    who_forwarded_chat_id=int("-100" + str(message.chat.id)),
                    who_forwarded_chat_title=message.chat.title,
                    who_forwarded_chat_username=message.chat.username
                ),
                messages=messages_list
            )
            fwd_msg_data = await qc.create_forwarded_message(message_id=message.fwd_from.channel_post,
                                                             chat_id=int("-100" + str(channel_id)),
                                                             chat_title=channel_title,
                                                             chat_username=channel_username,
                                                             who_forwarded_chat_id=int("-100" + str(message.chat.id)),
                                                             who_forwarded_chat_title=message.chat.title,
                                                             who_forwarded_chat_username=message.chat.username)
            messages_list.append(dict(
                id=fwd_msg_data.id,
                message_id=message.id,
            ))

            json_msg = json.dumps(to_json)
            msg = await event.forward_to(BOT_ID)
            await client.send_message(BOT_ID, json_msg, reply_to=msg)

        @client.on(events.NewMessage(forwards=False))
        async def forward_usual_message(event):
            if not(isinstance(event.message.peer_id, PeerChannel)):
                return
            if event.media:
                channel_messages = await client(functions.channels.GetMessagesRequest(
                    channel=event.message.chat,
                    id=[InputMessageID(event.message.id - 1), InputMessageID(event.message.id + 1)]
                ))

                previous_message = channel_messages.messages[0]
                next_message = channel_messages.messages[1]
                if (previous_message.date == event.message.date or next_message.date == event.message.date) \
                        and (previous_message.media or next_message.media):
                    return
            try:
                # TODO: ValueError: Could not find the input entity for PeerUser(user_id=5292056351) (PeerUser)
                # ОБРАБОТАТЬ!!!!
                # msg = await client.send_message(
                #     BOT_ID,
                #     message=event.message,
                #     formatting_entities=event.entities
                # )
                await event.forward_to(BOT_ID)
            except MessageIdInvalidError as e:
                logging.info(e)

        # @client.on(events.NewMessage(forwards=True))
        # async def send_forwarded_message(event):
        #     if not(isinstance(event.message.peer_id, PeerChannel)):
        #         return
        #     message = event.message
        #     await qc.create_forwarded_message(message_id=message.id,
        #                                       who_forwarded_chat_id=message.chat.id,
        #                                       who_forwarded_chat_name=message.chat.title,
        #                                       who_forwarded_chat_username=message.chat.username)
        #     await client.send_message(
        #         BOT_ID,
        #         file=event.media,  # event.messages is a List - meaning we're sending an album
        #         message=event.message,  # get the caption message from the album
        #     )

        print("Client is running!")
        await client.run_until_disconnected()

async def clients_main():
    print("Setup connection with PostgreSQL")
    await db.set_bind(POSTGRES_URI)
    # await db.gino.create_all()
    clients_data = await Client.get_clients()

    print("Total clients to run: %s" % len(clients_data))

    clients = [
        TelegramClient("session_" + str(client.telegram_id), client.api_id, client.api_hash) for client in clients_data
    ]

    await asyncio.gather(
        *[run_client(client) for client in clients],
    )


if __name__ == '__main__':
    asyncio.run(clients_main())
