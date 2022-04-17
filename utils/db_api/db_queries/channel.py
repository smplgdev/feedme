import logging
from typing import List

from asyncpg import UniqueViolationError
from sqlalchemy import or_, and_

from utils.db_api.schemas.channels import Channels
from utils.db_api.schemas.clients import Client
from utils.db_api.schemas.followers import Followers
from utils.db_api.schemas.users import User


class Channel:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id


    async def get(self, **kwargs):
        if len(kwargs) == 0:
            return await Channels.query.where(Channels.telegram_id == self.telegram_id).gino.first()
        return await Channels.query.where(or_(*[kwarg for kwarg in kwargs])).gino.first()

    async def add(self, client_telegram_id, title: str = None, username: str = None):
        channel = Channels(
                telegram_id=self.telegram_id,
                title=title,
                username=username,
                client_telegram_id=client_telegram_id
            )
        try:
            await channel.create()
        except UniqueViolationError:
            return True
        return True

    @staticmethod
    async def get_channel_entity(client, channel_info):
        try:
            return await client.get_input_entity(channel_info)
        except ValueError as e:
            logging.info(e)
            return False
        except TypeError as e:
            logging.info(e)
            return False

    async def select_client(self, channel_username: str = None, channel_invite_link: str = None, channel_hash = None):
        is_following = await Client.query.where(and_(or_(self.telegram_id == Channels.telegram_id,
                                                    Channels.username == (channel_username or 'None'),
                                                    Channels.invite_link == (channel_invite_link or 'None'),
                                                    Channels.private_hash == (channel_hash or 'None')),
                                                    User.is_active == True,)).gino.first()
        if is_following:
            return is_following

        clients_data = await Client.query.where(Client.is_running == True).gino.all()
        for i in range(len(clients_data) - 1, -1, -1):
            channels = await Channels.query.where(clients_data[i].telegram_id == Channels.client_telegram_id).gino.all()
            if len(channels) < 495:
                return clients_data[i]

        return None

    async def get_followed_users(self):
        return await Followers.query.where(Followers.channel_id == self.telegram_id).gino.all()

    @staticmethod
    async def get_all_channels() -> List[Channels]:
        return await Channels.query.gino.all()

    @staticmethod
    async def get_dublicated_channels() -> set:
        channels = await Channel.get_all_channels()
        ids = set()
        dublicates = set()
        for channel in channels:
            if channel.telegram_id in ids:
                dublicates.add([channel.telegram_id, channel.client_telegram_id, channel.title])
                await Channels(id=channel.id).delete()
            else:
                ids.add(channel.telegram_id)
        return dublicates
