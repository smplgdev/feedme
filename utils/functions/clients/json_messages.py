import json

from telethon.tl import functions
from telethon.tl.types import InputChannel

from utils.db_api.db_queries.channel import Channel
from utils.db_api.db_queries.client import Client
from utils.db_api.db_queries.follower import Follower
from utils.db_api.schemas.channels import Channels


async def deserialize_bot_json(client, json_msg) -> (Channels, int, bool, int):
    json_dict = json.loads(json_msg)
    follower_id = json_dict['message']['from_user_id']
    message_id = json_dict['message']['message_id']
    channel_id = json_dict['channel']['id']
    channel_username = json_dict['channel']['username']
    channel_title = json_dict['channel']['title']
    channel_private_hash = json_dict['channel']['private_hash']
    channel_invite_link = json_dict['channel']['invite_link']

    client_id = json_dict['client']['id']

    channel_entity = await Channel.get_channel_entity(client,
                                                      channel_username or channel_invite_link)

    channel = await Client(client_id).start_tracking_channel_or_pass(client,
                                                                     client_id,
                                                                     channel_entity,
                                                                     channel_invite_link,
                                                                     channel_private_hash)

    is_following = await Follower(follower_id).get_follower(channel.telegram_id)

    return channel, follower_id, is_following, message_id


async def serialize_message_to_bot(follower_id: int, channel: Channels, message_id: int, status: str = None):
    follower_dict = {
        "id": follower_id,
        "message_id": message_id,
        "status": status
    }
    channel_dict = {
        "id": channel.telegram_id,
        "title": channel.title,
        "username": channel.username,
        "invite_link": channel.invite_link,
        "private_hash": channel.private_hash
    }
    client_dict = {
        "id": channel.client_telegram_id,
    }

    to_json = {"follower": follower_dict, "channel": channel_dict, "client": client_dict}
    json_message = json.dumps(to_json)
    return json_message


async def json_message_data(event) -> str:
    channel = dict(
        id=int("-100" + str(event.message.peer_id.channel_id)),
    )
    message = dict(
        id=event.message.id,
        is_forwarded=bool(event.message.fwd_from)
    )
    forward_data = dict()
    to_json = dict(
        new_message=True,
        message=message,
        channel=channel,
        forward_data=forward_data
    )
    json_msg = json.dumps(to_json)
    return json_msg
