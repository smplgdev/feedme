from utils.db_api.schemas.forwarded_messages import ForwardMessage
from utils.db_api.schemas.shortened_messages import ShortenedMessage


async def create_shortened_message(full_text: str) -> ShortenedMessage.id:
    message = ShortenedMessage(
        full_text=full_text
    )
    await message.create()
    return message.id


async def get_full_message_from_shortened(msg_id: int) -> str:
    message = await ShortenedMessage.query.where(ShortenedMessage.id == msg_id).gino.first()
    return message.full_text


async def get_forwarded_message_query(message_id: int) -> ForwardMessage:
    return await ForwardMessage.query.where(message_id == ForwardMessage.id).gino.first()


async def create_forwarded_message(message_id: int,
                                   chat_id: int,
                                   chat_username: str,
                                   chat_title: str,
                                   who_forwarded_chat_id,
                                   who_forwarded_chat_title: int,
                                   who_forwarded_chat_username: str):
    forwarded_message = ForwardMessage(
        message_id=message_id,
        chat_id=chat_id,
        chat_username=chat_username,
        chat_title=chat_title,
        who_forwarded_chat_id=who_forwarded_chat_id,
        who_forwarded_chat_title=who_forwarded_chat_title,
        who_forwarded_chat_username=who_forwarded_chat_username
    )
    await forwarded_message.create()
    return forwarded_message
