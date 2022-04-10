from sqlalchemy import Column, BigInteger, String, sql, Boolean, Date, DateTime

from utils.db_api.db_gino import TimedBaseModel


class ForwardMessage(TimedBaseModel):
    __tablename__ = 'forwarded_messages'

    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    chat_username = Column(String(32))
    chat_title = Column(String(100))
    who_forwarded_chat_id = Column(BigInteger)
    who_forwarded_chat_title = Column(String(100))
    who_forwarded_chat_username = Column(String(32))

    is_sent = Column(Boolean, default=False)

    query: sql.Select

