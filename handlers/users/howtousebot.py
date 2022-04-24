from aiogram import types
from aiogram.dispatcher.filters import CommandHelp

from handlers.users.start import how_to_use_text
from loader import dp


@dp.message_handler(CommandHelp())
@dp.message_handler(text=how_to_use_text)
async def how_to_use_bot_handler(message: types.Message):
    await message.answer("""💡 Чтобы информация не повторялась, можно отписаться или заархивировать добавленные в ленту \
каналы, так как все сообщения теперь находятся в вашей ленте.

📌 Кроме того, советуем закрепить @FeedMeRobot поверху всех чатов, чтобы его не потерять.
Сделать это так же очень просто:
- найти FEEDME в списке ваших чатов
- выделить и закрепить""")
