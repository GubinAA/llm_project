import json
import configparser
from datetime import datetime, timedelta
import asyncio
from telethon.sync import TelegramClient
from telethon.errors import AuthKeyError
import os

# Чтение конфигурации
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
channels = config['telegram']['channels'].split(',')
session_name = 'my_session'

def fetch_telegram_messages(
    api_id,
    api_hash,
    channels_list,
    session_name='my_session',
    output_file='messages.json',
    days_interval=7
):
    """
    Скачиваем сообщения из заданных каналов за последние days_interval дней.

    Подход:
      - datetime.utcnow() создаёт "naive"-дату (без tzinfo),
      - у message.date убираем tzinfo через .replace(tzinfo=None),
      - как только встречаем сообщение, которое старше cutoff_date (naive),
        прерываем цикл (break).
      - reverse=True — идём от самых старых к новым (и останавливаемся по условию).
    """
    # cutoff_date — наивная дата (без tzinfo)
    cutoff_date = datetime.utcnow() - timedelta(days=days_interval)
    all_messages = []

    # Проверка на существование файла сессии
    if not os.path.exists(f"{session_name}.session"):
        print(f"Файл сессии {session_name}.session не найден. Будет создана новая сессия.")
    else:
        print(f"Файл сессии {session_name}.session найден. Используется существующая сессия.")

    try:
        with TelegramClient(session_name, api_id, api_hash) as client:
            print("Сессия успешно загружена. Готово к работе.")
            for channel in channels_list:
                channel = channel.strip()
                print(f"Fetching messages from channel: {channel}")

                for message in client.iter_messages(channel, reverse=True):
                    # Убираем tzinfo у даты сообщения, чтобы сравнивать "naive" с "naive"
                    msg_date_naive = message.date.replace(tzinfo=None)

                    # Если сообщение старше нужного порога — прекращаем
                    if msg_date_naive < cutoff_date:
                        break

                    if message.text:
                        all_messages.append({
                            'id': message.id,
                            'text': message.text,
                            'date': str(message.date),
                            'channel': channel
                        })

                    # Небольшая задержка, чтобы не попасть под rate-limit
                    asyncio.sleep(0.1)

            print(f"Total messages fetched: {len(all_messages)}")

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_messages, f, ensure_ascii=False, indent=2)

            return all_messages
    except AuthKeyError:
        print("Файл сессии повреждён или недействителен. Удалите файл сессии и попробуйте снова.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    fetch_telegram_messages(api_id, api_hash, channels, session_name, 'messages.json', 7)
