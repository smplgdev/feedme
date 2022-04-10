from sqlalchemy import Column, BigInteger, String, sql, Boolean, ForeignKey

from utils.db_api.db_gino import TimedBaseModel


class Followers(TimedBaseModel):
    __tablename__ = "followers"

    id = Column(BigInteger, primary_key=True)
    follower_telegram_id = Column(ForeignKey('users.telegram_id'))
    channel_id = Column(ForeignKey('channels.telegram_id'))

    is_tracking = Column(Boolean, default=True)

    query: sql.Select
