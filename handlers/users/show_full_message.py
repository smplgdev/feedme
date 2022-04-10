from aiogram import types

from keyboards.inline.show_full_text_button import shortened_message_callback
from loader import dp
from utils.db_api import quick_commands as qc


@dp.callback_query_handler(shortened_message_callback.filter())
async def show_full_message_handler(call: types.CallbackQuery, callback_data: dict):
    message_id = int(callback_data.get("msg_id"))
    message_text = await qc.get_full_message_from_shortened(message_id)
    await call.message.delete_reply_markup()
    await call.message.edit_text(message_text, disable_web_page_preview=True)
