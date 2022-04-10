from handlers.clients.follow_status import cannot_join_channel_text, already_following_text, following_limit_text, \
    success_text
from utils.db_api.db_queries.follower import Follower
from utils.db_api.db_queries.telegram_user import TelegramUser
from utils.db_api.schemas.channels import Channels
from utils.db_api.schemas.followers import Followers


async def get_following_status(follower_id: int, channel: Channels, is_following: bool = False) -> str:
    status = None
    if not channel:
        status = cannot_join_channel_text
    if is_following:
        status = already_following_text
    try:
        is_vip = await TelegramUser(follower_id).is_vip()
    except AttributeError:
        is_vip = False
    if not is_vip:
        count = await Follower(follower_id).count_following_channels()
        if count > 50:
            status = following_limit_text

    if not status:
        status = success_text

    return status