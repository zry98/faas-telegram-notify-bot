import os
import binascii
from base64 import b64decode
import telegram


BOT_TOKEN = os.environ['BOT_TOKEN']
USER_ID = int(os.environ['USER_ID'])


def main(request):
    bot = telegram.Bot(token=BOT_TOKEN)

    if request.form and 'msg' in request.form:
        args = request.form
    elif request.args and 'msg' in request.args:
        args = request.args
    else:
        return 'null'

    if 'b64' in args and (args.get('b64') == 'true' or args.get('b64') == '1'):
        try:
            message = b64decode(args.get('msg')).decode('utf-8')
        except binascii.Error:
            message = 'An error occurred while decoding the message'
    else:
        message = args.get('msg')

    message = message if message else '(Blank message)'

    bot.send_message(chat_id=USER_ID, text=message)
