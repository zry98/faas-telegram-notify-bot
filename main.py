from base64 import b64decode
from os import environ
from time import time
import ipinfo
import telegram
from google.cloud import firestore

BOT_TOKEN: str = environ['BOT_TOKEN']
USER_ID: str = environ['USER_ID']
IPINFO_TOKEN: str = environ['IPINFO_TOKEN']
DB: firestore.Client


def log(type: str, data: dict, error_type: str = '') -> None:
    """Write log to the Firestore DB.

    Args:
        type (str): Log type.
        data (dict): Data to write.
        error_type (str): Type of error if it's a error log.

    Returns:
        None

    """
    if type == 'error':
        doc_ref = DB.collection('notify-bot').document('error').collection(error_type).document(str(time()))
    else:
        doc_ref = DB.collection('notify-bot').document('archive').collection(type).document(str(time()))

    doc_ref.set(data)


def main(request) -> str:
    """Main function for Google Cloud Functions to execute.
    """
    global DB
    try:
        DB = firestore.Client()
        bot = telegram.Bot(token=BOT_TOKEN)
    except:
        return 'ERROR'

    if request.method == 'POST' and request.is_json:
        json = request.get_json()
        log('requests', json)
        message = parse_json(json)
    elif request.method == 'POST' and 'msg' in request.form:
        log('requests', request.form.to_dict())
        message = parse_text(request.form)
    elif request.method == 'GET' and 'msg' in request.args:
        log('requests', request.args.to_dict())
        message = parse_text(request.args)
    else:
        return 'ERROR'

    if not message:
        return 'ERROR'

    bot.send_message(chat_id=USER_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    return 'OK'


def parse_text(params) -> str:
    """Parse a plain text message GET request.

    Args:
        params (flask.request.args): GET request parameters.

    Returns:
        message (str): The message for the user.

    """
    if 'b64' in params and (params.get('b64') == 'true' or params.get('b64') == '1'):
        try:
            message = b64decode(params.get('msg')).decode('utf-8')
        except:
            return ''
    else:
        message = params.get('msg')

    log('messages', {'type': 'text', 'message': message})

    return message


def parse_json(json: dict) -> str:
    """Parse a JSON message POST request.

    Args:
        request (dict): The POST request.

    Returns:
        message (str): The message for the user.

    """
    if json['type']:
        if json['type'] == 'SMS':
            message = build_sms_message(json['data'])
        elif json['type'] == 'ALERT':
            message = build_alert_message(json['data'])
        else:
            message = json['data']['text']
        log('messages', {'type': json['type'], 'message': message})
    else:
        message = json['data']['text']
        log('messages', {'type': 'text', 'message': message})

    return message


def build_sms_message(data) -> str:
    """Build a SMS forwarding message.
    """
    message = '*SMS*\n' \
              '_From: {}_\n' \
              '_At: {}_\n' \
              '\n' \
              '{}' \
        .format(data['from'], data['datetime'], data['text'])

    return message


def build_alert_message(data) -> str:
    """Build an alert message.
    """
    message = '*ALERT*\n' \
              '_From: {}_\n' \
              '_At: {}_\n' \
              '\n' \
        .format(data['from'], data['datetime'])

    if data['type'] == 'SSH':
        message += 'SSH login: {}\n' \
                   'IP address: {}\n' \
                   'IP geolocation: {}' \
            .format(data['username'], data['ip'], get_ip_geolocation(data['ip']))

    elif data['type'] == 'PVE':
        message += 'PVE login: {}\n' \
                   'IP address: {}\n' \
                   'IP geolocation: {}' \
            .format(data['username'], data['ip'], get_ip_geolocation(data['ip']))

    elif data['type'] == 'Bitwarden':
        message += 'Bitwarden login: {}\n' \
                   'IP address: {}\n' \
                   'IP geolocation: {}' \
            .format(data['username'], data['ip'], get_ip_geolocation(data['ip']))

    else:
        message += data['text']

    return message


def get_ip_geolocation(ip: str) -> str:
    """Get IP Geolocation using ipinfo.io API.

    Args:
        ip (str): The IP address to query.

    Returns:
        info (str): Geolocation info of the IP address.

    """
    try:
        handler = ipinfo.getHandler(IPINFO_TOKEN)
        details = handler.getDetails(ip)
    except Exception as e:
        log_data = {'message': str(e)}
        log('error', log_data, 'get_ip_geolocation')
        return '[error]'

    info = '{}, {}, {}'.format(details.city, details.region, details.country)

    return info
