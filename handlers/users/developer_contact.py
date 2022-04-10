from aiogram import types
from aiogram.dispatcher.filters import Command

from handlers.users.start import developer_text
from loader import dp


@dp.message_handler(Command("developer"))
@dp.message_handler(text=developer_text)
async def get_developer_contact_info_handler(message: types.Message):
    await message.answer("Есть вопросы и пожелания по развитию проекта? Или хотите бота на заказ?"
                         "\n\nОбращайтесь ко мне: @vxlone")
