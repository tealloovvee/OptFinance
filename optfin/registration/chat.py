

import requests

class TelegramAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def send_message(self, chat_id, text):
        url = self.base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=data)
        return response.json()