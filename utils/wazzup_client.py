import requests
from config import Config

class WazzupClient:
    def __init__(self):
        self.api_key = Config.WAZZUP_API_KEY
        self.api_url = Config.WAZZUP_API_URL
        self.channel_id = Config.WAZZUP_CHANNEL_ID

    def send_message(self, chat_id, message_text):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "channelId": self.channel_id,
            "chatType": "whatsapp",
            "chatId": chat_id,
            "text": message_text
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            print("Ответ от Wazzup:", response.json())
            return response.json()
        except requests.exceptions.HTTPError as e:
            print("Ошибка HTTP:", e)
        except requests.exceptions.RequestException as e:
            print("Ошибка при отправке сообщения в Wazzup:", e)