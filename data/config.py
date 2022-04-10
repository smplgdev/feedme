from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")

PG_USER = env.str("PG_USER")
PG_PASSWORD = env.str("PG_PASSWORD")
DATABASE = env.str("DATABASE")
DB_HOST = env.str("DB_HOST")

BOT_USERNAME = env.str("BOT_USERNAME")
BOT_ID = env.int("BOT_ID")

CLIENTS_IDS = list()

POSTGRES_URI = f'postgresql://{PG_USER}:{PG_PASSWORD}@{DB_HOST}/{DATABASE}'
