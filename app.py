from aiogram import executor

import middlewares, filters, handlers

from data.config import CLIENTS_IDS
from loader import dp
from utils.db_api import db_gino
from utils.db_api.db_gino import db
from utils.db_api.db_queries.client import Client
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

    await on_startup_notify(dispatcher)

    await db_gino.on_startup(dispatcher)

    await db.gino.create_all()

    clients = await Client.get_clients()
    for client in clients:
        CLIENTS_IDS.append(client.telegram_id)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
