import datetime
from typing import List

from aiogram import Dispatcher
from gino import Gino
import sqlalchemy as sa
from sqlalchemy import Column, DateTime

from data.config import POSTGRES_URI

db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}"
                              for name, value in values.items())
        return f"<{model} {values_str}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = Column(DateTime(True), server_default=db.func.now())
    updated_at = Column(DateTime(True),
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow,
                        server_default=db.func.now())


async def on_startup(dispatcher: Dispatcher):
    print("Установка соединения с PostgreSQL")
    await db.set_bind(POSTGRES_URI)
