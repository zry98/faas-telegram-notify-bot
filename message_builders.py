from logger import log
from os import environ
import ipinfo

IPINFO_TOKEN: str = environ['IPINFO_TOKEN']


def build_sms_message(data) -> str:
    """Build a SMS forwarding message.
    """
    message = '<b>SMS</b>\n' \
              '<i>From: {}</i>\n' \
              '<i>At: {}</i>\n' \
              '\n' \
              '{}' \
        .format(data['from'], data['datetime'], plain_text(data['text']))

    return message


def build_alert_message(data) -> str:
    """Build an alert message.
    """
    message = '<b>ALERT</b>\n' \
              '<i>From: {}</i>\n' \
              '<i>At: {}</i>\n' \
              '\n' \
        .format(data['from'], data['datetime'])

    if data['type'] == 'SSH':
        message += 'SSH Login: {}\n' \
                   'IP Address: {}\n' \
                   'IP Geolocation: {}' \
            .format(data['username'], data['ip'], get_ip_geolocation(data['ip']))

    elif data['type'] == 'PVE':
        message += 'PVE Login: {}\n' \
                   'IP Address: {}\n' \
                   'IP Geolocation: {}' \
            .format(data['username'], data['ip'], get_ip_geolocation(data['ip']))

    elif data['type'] == 'Bitwarden':
        message += 'Bitwarden Login: {}\n' \
                   'IP Address: {}\n' \
                   'IP Geolocation: {}' \
            .format(data['username'], data['ip'], get_ip_geolocation(data['ip']))

    else:
        message += plain_text(data['text'])

    return message


def plain_text(text: str) -> str:
    return text \
        .replace('<', '&lt;') \
        .replace('>', '&gt;') \
        .replace('&', '&amp;')


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
        return '[ERROR]'

    info = '{}, {}, {}'.format(details.city, details.region, details.country)

    return info
