import json
import configparser
from datetime import datetime, timezone, timedelta
import asyncio
from telethon import TelegramClient
from telethon.errors import AuthKeyError
import os

# Получаем абсолютный путь к директории скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(SCRIPT_DIR, 'my_session')

# Глобальный клиент для переиспользования сессии
client = None

async def get_client(api_id, api_hash):
    """
    Создает или возвращает существующий клиент
    """
    global client
    
    print(f"Текущая директория: {SCRIPT_DIR}")
    print(f"Путь к файлу сессии: {SESSION_PATH}.session")
    print(f"Файл сессии существует: {os.path.exists(f'{SESSION_PATH}.session')}")
    
    if client is None or not client.is_connected():
        try:
            print("Создаем новый клиент...")
            client = TelegramClient(SESSION_PATH, api_id, api_hash)
            print("Начинаем процесс подключения...")
            await client.connect()
            
            if not await client.is_user_authorized():
                print("Требуется авторизация...")
                await client.start()
            else:
                print("Пользователь уже авторизован")
                
            print("Подключение успешно установлено")
        except Exception as e:
            print(f"Ошибка при подключении: {e}")
            raise
            
    return client

async def fetch_telegram_messages(
    api_id,
    api_hash,
    channels_list,
    output_file='messages.json',
    days_interval=7
):
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_interval)
    all_messages = []

    try:
        # Используем существующий клиент или создаем новый
        client = await get_client(api_id, api_hash)
        print("Сессия активна. Готово к работе.")

        for channel in channels_list:
            channel = channel.strip()
            print(f"Получаем сообщения из канала: {channel}")

            try:
                messages = client.iter_messages(
                    channel,
                    offset_date=cutoff_date,
                    reverse=False,
                    limit=None,
                    wait_time=2  # Увеличиваем задержку между запросами
                )

                async for message in messages:
                    if message.text:
                        all_messages.append({
                            'id': message.id,
                            'text': message.text,
                            'date': str(message.date),
                            'channel': channel,
                            'views': getattr(message, 'views', 0),
                            'forwards': getattr(message, 'forwards', 0)
                        })
                    
                    # Увеличиваем задержку между сообщениями
                    await asyncio.sleep(0.5)

                # Добавляем задержку между каналами
                await asyncio.sleep(2)

            except Exception as e:
                print(f"Ошибка при получении сообщений из канала {channel}: {e}")
                # Делаем паузу перед следующим каналом при ошибке
                await asyncio.sleep(5)
                continue

        print(f"Всего получено сообщений: {len(all_messages)}")

        all_messages.sort(key=lambda x: datetime.fromisoformat(x['date']), reverse=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_messages, f, ensure_ascii=False, indent=2)

        return all_messages

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

def main():
    # Чтение конфигурации
    config = configparser.ConfigParser()
    
    # Проверяем существование файла конфигурации
    if not os.path.exists('config.ini'):
        print("Ошибка: Файл config.ini не найден")
        return
        
    config.read('config.ini', encoding='utf-8')
    
    try:
        api_id = int(config['telegram']['api_id'])
        api_hash = config['telegram']['api_hash']
        channels = [channel.strip() for channel in config['telegram']['channels'].split(',')]

        # Запускаем асинхронную функцию с правильным количеством аргументов
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fetch_telegram_messages(
            api_id, 
            api_hash, 
            channels, 
            'messages.json', 
            7
        ))
    except KeyError as e:
        print(f"Ошибка: Отсутствует обязательный параметр в config.ini: {e}")
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}")

if __name__ == '__main__':
    main()
