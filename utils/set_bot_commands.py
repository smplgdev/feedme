from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("channels", "Показать список моих каналов"),
            types.BotCommand("developer", "Написать разработчику бота"),
            types.BotCommand("help", "О боте"),
            types.BotCommand("start", "Перезапустить бота (в случае зависания, неполадок)"),
        ]
    )
