from sqlalchemy import Column, BigInteger, String, sql, Boolean

from utils.db_api.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)

    username = Column(String(32))

    deep_link = Column(String(20), default=None)
    is_vip = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)

    query: sql.Select
