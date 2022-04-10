import json

from aiogram import types

from filters.client_filter import ClientFilter
from handlers.users.start import get_menu_markup
from loader import dp, bot

already_following_text = "Already Following!"
following_limit_text = "Too many followings!"
success_text = "Success!!"
unexpected_error_text = "Unexpected Error :("
cannot_join_channel_text = "Cannot join channel!"

def decode_message(json_msg):
    json_dict = json.loads(json_msg)

    follower_id = json_dict['follower']['id']
    message_id = json_dict['follower']['message_id']
    follow_status = json_dict['follower']['status']

    channel_name = json_dict['channel']['title']
    channel_username = json_dict['channel']['username']

    if follow_status == success_text:
        return follower_id, message_id, f"✅ <b>Вы успешно подписались на канал «{channel_name}»!</b>"
    elif follow_status == already_following_text:
        return follower_id, message_id, f"Вы уже подписаны на канал «{channel_name}»!"
    elif follow_status == following_limit_text:
        return follower_id, message_id, "Вы достигли лимита подписок :(\nРесурсы сервера не бесконечные." \
               f"Чтобы подписаться на канал «{channel_name}», сперва отпишитесь от " \
               "какого-нибудь другого"
    elif follow_status == cannot_join_channel_text:
        return follower_id, message_id, f"<b>У меня не получилось подписаться на этот канал.</b>\n" \
                                        f"Вероятнее всего, он закрытый. Пожалуйста, добавьте другие каналы"
    elif follow_status == unexpected_error_text:
        return follower_id, message_id, f"Произошла непредвиденная ошибка! :( Повторите попытку."
    else:
        return follower_id, message_id, f"Произошла непредвиденная ошибка! :( Повторите попытку."


@dp.message_handler(ClientFilter(), regexp=r'^{"follower":')
async def answer_to_user(message: types.Message):
    json_msg = message.text
    markup = get_menu_markup()
    follower_id, message_id, text = decode_message(json_msg)
    await bot.send_message(follower_id,
                           text,
                           reply_to_message_id=message_id,
                           reply_markup=markup)