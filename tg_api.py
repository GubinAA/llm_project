#Telegram API Setup
from telethon.sync import TelegramClient
import json
import configparser
import asyncio

# Загружаем конфигурацию из файла config.ini
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['telegram']['api_id'] # Получаем id из файла config
api_hash = config['telegram']['api_hash'] # Получаем hash из файла config
channel_username = config['telegram']['channel_username']  # Имя публичного канала

# Собираем сообщения с публичного tg канала
def fetch_telegram_messages(api_id, api_hash, channel_username, output_file='messages.json'):
    with TelegramClient('my_session', api_id, api_hash) as client:
        messages = []
        for message in client.iter_messages(channel_username):
            if message.text:
                messages.append({
                    'id': message.id,
                    'text': message.text,
                    'date': str(message.date)
                })
            asyncio.sleep(1)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        print(f"Fetched {len(messages)} messages and saved to {output_file}.")

fetch_telegram_messages(api_id, api_hash, channel_username)