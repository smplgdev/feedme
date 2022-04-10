from sqlalchemy import Column, BigInteger, String, sql, Boolean

from utils.db_api.db_gino import TimedBaseModel


class Client(TimedBaseModel):
    __tablename__ = "clients"

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)

    api_id = Column(BigInteger)
    api_hash = Column(String(32))

    is_running = Column(Boolean, default=False)

    query: sql.Select
