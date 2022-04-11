from sqlalchemy import and_
from telethon.tl import functions

from utils.db_api.db_gino import db
from utils.db_api.db_queries.telegram_user import TelegramUser
from utils.db_api.schemas.channels import Channels
from utils.db_api.schemas.followers import Followers


class Follower(TelegramUser):
    async def get_follower(self, channel_id: int):
        return await Followers.query.where(and_(self.telegram_id == Followers.follower_telegram_id,
                                                channel_id == Followers.channel_id)).gino.first()

    async def add_follower(self, channel_id: int):
        follower = Followers(
            follower_telegram_id=self.telegram_id,
            channel_id=channel_id
        )
        await follower.create()
        return follower

    async def is_following(self, channel_id: int):
        is_following = await Followers.query.where(and_(Followers.channel_id == channel_id,
                                                        Followers.follower_telegram_id == self.telegram_id)).gino.first()
        return bool(is_following)

    async def delete_follower(self, channel_id: int):
        follower = await Followers.query.where(and_(Followers.follower_telegram_id == self.telegram_id,
                                                    Followers.channel_id == channel_id)).gino.first()
        if follower:
            await follower.delete()

    async def all_following_channels(self):
        return await Followers.join(Channels).select()\
            .where(Followers.follower_telegram_id == self.telegram_id).gino.all()

    async def count_following_channels(self):
        return await (db.select([db.func.count()])
                      .where(Followers.follower_telegram_id == self.telegram_id)
                      .gino
                      .scalar())

    async def start_tracking_channel_or_pass(self,
                                             client,
                                             client_id: int,
                                             channel_entity,
                                             channel_id: int = -1,
                                             channel_title: str = None,
                                             channel_username: str = None,
                                             channel_invite_link: str = None):
        if not channel_title or not channel_username:
            chatfull = await client(functions.channels.GetFullChannelRequest(channel_entity))
            channel_title = chatfull.chats[0].title
            channel_username = chatfull.chats[0].username

    async def get_following_channels(self):
        return await Followers.join(Channels).select().where(
            Followers.follower_telegram_id == self.telegram_id).gino.all()
