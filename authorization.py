import asyncio
import json

from telethon import TelegramClient, events
from telethon.tl import functions
from telethon.tl.types import PeerChannel, InputMessageID, PeerUser, PeerChat, \
    MessageMediaPoll

from data.config import BOT_ID, POSTGRES_URI, BOT_USERNAME
from handlers.clients.follow_status import success_text
from utils.db_api.db_gino import db
from utils.db_api.db_queries.channel import Channel
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
            await client.send_message(BOT_USERNAME, message_text)

        @client.on(events.Album())
        async def send_album(event):
            message = event.messages[0]

            msg = await client.send_message(
                BOT_USERNAME,
                file=event.messages,
                message=list(map(lambda a: str(a.message), event.messages),
            ))

            await forward_usual_message(event, message, msg[0])


        @client.on(events.NewMessage(incoming=True))
        async def forward_usual_message(event, message=None, msg=None):
            if msg is None:
                message = event.message

            if not(isinstance(message.peer_id, PeerChannel)):
                return

            is_album = bool(msg)
            with_media = bool(message.media)

            if message.media and not msg:
                if isinstance(message.media, MessageMediaPoll):
                    msg = await event.forward_to(BOT_USERNAME)

                channel_messages = await client(functions.channels.GetMessagesRequest(
                    channel=message.chat,
                    id=[InputMessageID(message.id - 1), InputMessageID(message.id + 1)]
                ))

                previous_message = channel_messages.messages[0]
                next_message = channel_messages.messages[1]
                if not msg and (((previous_message.date == message.date) and previous_message.media) or
                               ((next_message.date == message.date) and next_message.media)):
                    return
            channel_id = int("-100" + str(message.peer_id.channel_id))
            channel_entity = await client.get_entity(channel_id)
            channel = await Channel(channel_id).get()
            if not channel:
                return
            if channel_entity.title != channel.title:
                await Channel(channel_id).update(title=channel_entity.title)
            if channel_entity.username != channel.username:
                await Channel(channel_id).update(username=channel_entity.username)

            if not msg:
                msg = await client.send_message(
                    BOT_USERNAME,
                    message,
                )

            forward_data = dict()
            is_fwd = False
            if message.fwd_from:
                is_fwd = True
                fwd_from = message.fwd_from
                from_id = fwd_from.from_id
                peer_type = None
                peer_id = None
                peer_name = None
                peer_username = None
                if isinstance(from_id, PeerChannel):
                    peer_type = 'PeerChannel'
                    peer_id = from_id.channel_id
                    entity = await client.get_entity(peer_id)
                    peer_name = entity.title
                    peer_username = entity.username
                elif isinstance(from_id, PeerUser):
                    peer_type = 'PeerUser'
                    peer_id = from_id.user_id
                    entity = await client.get_entity(peer_id)
                    peer_name = entity.first_name
                    peer_username = entity.username
                elif isinstance(from_id, PeerChat):
                    peer_type = 'PeerChat'
                    peer_id = from_id.chat_id
                    entity = await client.get_entity(peer_id)
                    peer_name = entity.title
                    peer_username = entity.username


                forward_data.update(
                    message=dict(
                        id=fwd_from.channel_post,
                    ),
                    peer=dict(
                        peer_type=peer_type,
                        id=peer_id,
                        name=peer_name,
                        username=peer_username,

                    )
                )

            to_json = dict(
                message=dict(
                    id=message.id,
                    is_forwarded=is_fwd
                ),
                channel=dict(
                    id=channel_id,
                    title=channel_entity.title,
                    username=channel_entity.username,
                    private_hash=channel.private_hash,
                    is_private=bool(channel.private_hash)
                ),
                forward_data=forward_data,
                with_media=with_media,
                is_album=is_album,
            )
            json_msg = json.dumps(to_json)

            await client.send_message(BOT_USERNAME, json_msg, reply_to=msg)
        print("Client is running!")
        client.parse_mode = None
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
