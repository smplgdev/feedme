from asyncpg import UniqueViolationError

from utils.db_api.schemas.users import User


class TelegramUser:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id

    @staticmethod
    async def get_all_users():
        return await User.query.gino.all()

    async def add(self, username, deep_link):
        """
        :param username: aiogram.types.Message.from_user.username
        :param deep_link: aiogram.types.Message.get_args()
        :return: An instance of the User that has been added to database
        """
        try:
            user = User(
                telegram_id=self.telegram_id,
                username=username,
                deep_link=deep_link
            )
            await user.create()
            return user
        except UniqueViolationError:
            pass

    async def delete(self):
        """
        :return: An instance of the User that has been removed
        """
        user = await User.get(self.telegram_id)
        await user.delete()
        return user

    async def is_vip(self):
        user = await User.query.where(User.telegram_id == self.telegram_id).gino.first()
        return user.is_vip
