from os import environ
from telegram import Bot as telegram_bot
from request_parser import parse

BOT_TOKEN: str = environ['BOT_TOKEN']
CHAT_ID: str = environ['CHAT_ID']


def main(request) -> str:
    """Main function for Google Cloud Functions to execute.
    """
    try:
        bot = telegram_bot(token=BOT_TOKEN)
    except:
        return 'ERROR'

    message = parse(request)

    if not message:
        return 'ERROR'

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')

    return 'OK'
