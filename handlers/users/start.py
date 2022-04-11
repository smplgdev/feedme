import asyncio

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.menu_keyboards import create_feed_markup, create_feed_callback
from loader import dp
from utils.db_api.db_queries.telegram_user import TelegramUser
from utils.strings import messages_text as msg

get_started_text = "Начать 🚀"
user_channels_text = "🗂 Мои каналы"
developer_text = "👨‍💻 Написать разработчику"
how_to_use_text = "Как использовать бота на все 💯"

how_to_subscribe_text = "Для отслеживания канала, <b>перешли мне из него любой пост</b> или его @username\n\n"


add_channels_callback = CallbackData("add_channels")

def get_started_markup() -> ReplyKeyboardMarkup():
    markup = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(get_started_text)
        ]
    ])
    return markup


def get_add_channels_markup():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("➕ Добавить каналы", callback_data=add_channels_callback.new())
        ]
    ])
    return markup

def get_menu_markup() -> ReplyKeyboardMarkup():
    markup = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(user_channels_text),
            KeyboardButton(developer_text)
        ],
        [
            KeyboardButton(how_to_use_text)
        ]
    ], resize_keyboard=True)
    return markup


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    deep_link = message.get_args()
    username = message.from_user.username
    user = TelegramUser(telegram_id)
    user_created = await user.add(username=username, deep_link=deep_link)
    if not user_created:
        # If launched bot before
        await message.answer("С возвращением!", reply_markup=get_menu_markup())
        return
    markup = create_feed_markup()
    await message.answer(msg.hello_user(message.from_user.first_name), reply_markup=markup)
    # await message.answer("Глеба самый жёсткий")

@dp.callback_query_handler(create_feed_callback.filter())
async def create_feed_handler(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await asyncio.sleep(0.5)
    await call.message.answer("Чтобы бот начал формировать ленту новостей, добавьте интересующие вас каналы.\n\n"
                              "Для этого выполните следующие шаги:\n"
                              "1. Зайдите в список всех ваших чатов\n"
                              "2. Откройте канал, который хотите добавить в ленту\n"
                              "3. Перешлите в «<b>FEEDME — Моя лента</b>» из канала любое сообщение"
                              " (или пришлите его @username)\n"
                              "Готово! Теперь все новые сообщения из этого канала будут появляться в FEEDME!"
                              "\n\n❗️<b>Обратите внимание, что в FEEDME нельзя добавлять "
                              "личные чаты и чаты для общения с другими людьми</b>")
    await call.message.answer_chat_action(types.ChatActions.TYPING)
    await asyncio.sleep(8)
    await call.message.answer("<b>Вы можете добавить до 50 каналов</b>. После добавления каналов в ленту, можно"
                              " отписаться от них или заархивировать их, ведь все новости будут появляться здесь!")
    await call.message.answer_chat_action(types.ChatActions.TYPING)
    await asyncio.sleep(5)
    await call.message.answer("<b>Отправьте боту каналы, на которые вы хотите подписаться:</b>")


@dp.message_handler(text=get_started_text)
async def instructions_message_handler(message: types.Message):
    markup = get_menu_markup()
    await message.answer(how_to_subscribe_text, reply_markup=markup)
