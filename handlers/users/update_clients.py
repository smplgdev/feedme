from aiogram import types
from aiogram.dispatcher.filters import Command

from data.config import ADMINS, CLIENTS_IDS
from loader import dp
from utils.db_api import quick_commands as qc
from utils.db_api.db_queries.client import Client


@dp.message_handler(Command("upd"), user_id=ADMINS)
async def update_clients_list(message: types.Message):
    msg = "Обновлённый список клиентов.\n"
    clients = await Client.get_clients()
    CLIENTS_IDS.clear()
    for client in clients:
        msg += str(client.telegram_id) + ". Is running: " + str(client.is_running) + "\n"
        CLIENTS_IDS.append(client.telegram_id)

    await message.answer(msg)

