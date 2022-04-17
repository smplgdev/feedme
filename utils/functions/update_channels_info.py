from utils.db_api.db_queries.channel import Channel
from utils.db_api.db_queries.client import Client


async def update_channels():
    clients = await Client.get_clients()
    for client in clients:
        channels = await Client(client.telegram_id).get_all_channels()
        pass

