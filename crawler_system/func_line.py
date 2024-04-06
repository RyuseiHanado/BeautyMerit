import requests
import logging

def send_line_message(access_token, message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }
    data = {
        'message': message
    }

    response = requests.post(url, headers=headers, data=data)
    return response


def notify_line(line_access_token, message):
    response = send_line_message(line_access_token, message)
    if response.status_code == 200:
        logging.info('LINEへのメッセージ通知に成功しました。： ' + message)
    else:
        logging.info('LINEへのメッセージ通知に失敗しました。： ' + message)
