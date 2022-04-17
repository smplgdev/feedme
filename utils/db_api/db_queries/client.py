import asyncio

from asyncpg import UniqueViolationError
from telethon.errors import UserAlreadyParticipantError, FloodWaitError
from telethon.tl import functions
from telethon.tl.functions.messages import ImportChatInviteRequest

from utils.db_api.db_queries.channel import Channel
from utils.db_api.schemas import clients
from utils.db_api.schemas.channels import Channels
from utils.db_api.schemas.clients import Client as ClientScheme


class Client:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id

    @staticmethod
    async def get_clients():
        return await ClientScheme.query.where(ClientScheme.is_running == True).gino.all()

    async def start_tracking_channel_or_pass(self,
                                             client,
                                             channel_entity,
                                             invite_link: str = None,
                                             private_hash: str = None) -> Channel | None:
        channel_id = None
        if private_hash:
            tries = 0
            while tries < 3:
                try:
                    channel = await client(ImportChatInviteRequest(private_hash))
                    channel_id = int("-100" + str(channel.chats[0].id))
                    break
                except UserAlreadyParticipantError:
                    channel = await Channels.query.where(private_hash == Channels.private_hash).gino.first()
                    return channel
                except FloodWaitError as e:
                    tries += 1
                    print("should wait " + str(e.seconds) + " seconds")
                    await asyncio.sleep(e.seconds)
                if tries == 3:
                    return
        else:
            channel_id = int("-100" + str(channel_entity.channel_id))
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
            invite_link=invite_link,
            private_hash=private_hash
        )
        try:
            await channel.create()
        except UniqueViolationError:
            pass
        return channel

    async def get_all_channels(self):
        return await ClientScheme.query.where(ClientScheme.telegram_id == self.telegram_id).gino.all()
