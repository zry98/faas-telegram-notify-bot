from base64 import b64decode
from logger import log
from message_builders import build_sms_message, build_alert_message


def parse(request) -> str:
    if request.method == 'POST' and request.is_json:
        json = request.get_json()
        log('requests', json)
        message = parse_json(json)

    elif request.method == 'POST' and 'msg' in request.form:
        log('requests', request.form.to_dict())
        message = parse_plain(request.form)

    elif request.method == 'GET' and 'msg' in request.args:
        log('requests', request.args.to_dict())
        message = parse_plain(request.args)

    else:
        message = ''

    return message


def parse_plain(params) -> str:
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
