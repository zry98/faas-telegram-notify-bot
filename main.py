from os import environ
from base64 import b64decode
import telegram

BOT_TOKEN = environ['BOT_TOKEN']
USER_ID = environ['USER_ID']


def main(request):
    bot = telegram.Bot(token=BOT_TOKEN)

    if request.method == 'POST' and request.is_json:
        message = parse_json(request)
    elif request.method == 'POST' and 'msg' in request.form:
        message = parse_text(request.form)
    elif request.method == 'GET' and 'msg' in request.args:
        message = parse_text(request.args)
    else:
        return 'ERROR'

    if not message:
        return 'ERROR'

    bot.send_message(chat_id=USER_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    return 'OK'


def parse_json(request) -> str:
    try:
        json = request.get_json()
    except:
        return ''

    if json['type']:
        message = '*' + json['type'] + '*\n'
        if json['type'] == 'SMS':
            message += '_From: ' + json['data']['from'] + '_\n\n'

        message += json['data']['text']
    else:
        return ''

    return message


def parse_text(params) -> str:
    if 'b64' in params and (params.get('b64') == 'true' or params.get('b64') == '1'):
        try:
            message = b64decode(params.get('msg')).decode('utf-8')
        except:
            return ''
    else:
        message = params.get('msg')

    return message
