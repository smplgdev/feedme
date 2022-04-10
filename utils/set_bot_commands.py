from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("channels", "Показать список моих каналов"),
            types.BotCommand("developer", "Написать что-нибудь разработчику бота"),
            types.BotCommand("help", "Расскажу, как лучше пользоваться ботом"),
            types.BotCommand("start", "Перезапустить бота"),
        ]
    )
