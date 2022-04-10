from sqlalchemy import Column, BigInteger, String, sql, Boolean, Date, DateTime

from utils.db_api.db_gino import TimedBaseModel


class ShortenedMessage(TimedBaseModel):
    __tablename__ = 'shortened_messages'

    id = Column(BigInteger, primary_key=True)
    full_text = Column(String(4092))

    query: sql.Select

