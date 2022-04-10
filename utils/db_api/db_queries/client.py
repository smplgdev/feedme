from asyncpg import UniqueViolationError
from telethon.tl import functions

from utils.db_api.db_queries.channel import Channel
from utils.db_api.schemas import clients
from utils.db_api.schemas.channels import Channels


class Client:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id

    @staticmethod
    async def get_clients():
        return await clients.Client.query.gino.all()

    async def start_tracking_channel_or_pass(self, client, channel_entity, invite_link: str = None) -> Channel | None:
        channel_id = int(f"-100{channel_entity.channel_id}")
        is_exists = await Channels.query.where(channel_id == Channels.telegram_id).gino.first()
        if is_exists:
            return is_exists
        try:
            channel = await client(functions.channels.JoinChannelRequest(channel_entity))
        except TypeError:
            return
        channel_title = channel.chats[0].title
        channel_username = channel.chats[0].username
        channel = Channels(
            telegram_id=channel_id,
            title=channel_title,
            username=channel_username,
            invite_link=invite_link
        )
        try:
            await channel.create()
        except UniqueViolationError:
            pass
        return channel
