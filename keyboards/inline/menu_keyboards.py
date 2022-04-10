from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

create_feed_callback = CallbackData("create_feed")

def create_feed_markup() -> InlineKeyboardMarkup():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("🔘 Создать ленту новостей", callback_data=create_feed_callback.new())
        ]
    ])
    return markup
