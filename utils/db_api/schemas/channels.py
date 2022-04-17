from sqlalchemy import Column, BigInteger, String, sql, Boolean, ForeignKey

from utils.db_api.db_gino import BaseModel


class Channels(BaseModel):
    __tablename__ = "channels"

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)

    title = Column(String(40))
    username = Column(String(32))
    invite_link = Column(String(60))
    private_hash = Column(String(50), default=None)

    client_telegram_id = Column(ForeignKey('clients.telegram_id'))

    query: sql.Select

