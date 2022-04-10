from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

shortened_message_callback = CallbackData("short_msg", "msg_id")


def get_show_full_markup(shortened_message_id: int) -> InlineKeyboardMarkup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Показать полностью", callback_data=shortened_message_callback.new(
                msg_id=shortened_message_id
            ))
        ]
    ])
