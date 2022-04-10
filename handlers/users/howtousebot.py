from aiogram import types
from aiogram.dispatcher.filters import CommandHelp

from handlers.users.start import how_to_use_text
from loader import dp


@dp.message_handler(CommandHelp())
@dp.message_handler(text=how_to_use_text)
async def how_to_use_bot_handler(message: types.Message):
    await message.answer("💡 Чтобы получить максимальный комфорт от использования бота, "
                         "рекомендем отписаться или заархивировать каналы после добавления их в ленту FeedMe, "
                         "чтобы очистить свой аккаунт от повторяющейся информации. "
                         "Так у вас все новости будут в @FeedMeRobot, "
                         "а на виду —  личные чаты\n\n"
                         "📌 Кроме того, советуем закрепить @FeedMeRobot поверху всех чатов, чтобы его не потерять"
                         "\n\nСписок команд бота:"
                         "\n/channels — Показать список моих каналов"
                         "\n/developer — Написать что-нибудь разработчику бота"
                         "\n/help — Вызвать данное сообщение"
                         "\n/start — Перезапустить бота")
