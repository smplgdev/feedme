import json

from telethon.tl.types import InputPhoto, InputDocument

from data.config import BOT_USERNAME


async def process_message_with_media_group(client,
                                           event,
                                           file_id,
                                           access_hash,
                                           file_reference,
                                           file_type: InputPhoto | InputDocument | None):
    to_json = {"ADDITIONAL_MESSAGE_DATA": {
        "file": {
            'id': file_id,
            'type': file_type.__name__,
        },
        'message': {
            'id': event.message.id,
            'caption': event.message.text,
            'date': str(event.message.date.strftime("%Y-%m-%d %H:%M:%S")),
        },
        "channel": {
            'id': event.message.chat_id,
        }
    }}
    caption = json.dumps(to_json)
    await client.send_file(BOT_USERNAME,
                           file_type(id=file_id, access_hash=access_hash, file_reference=file_reference), # It's OK.
                           caption=caption)


async def get_post_group(client, event):
    pass
