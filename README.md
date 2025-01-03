# **Investment News Assistant (AI RAG-проект)**

## **Описание проекта**
**Investment News Assistant** — это учебный проект, реализующий Retrieval-Augmented Generation (RAG) для получения новостей и формирования ответов на вопросы пользователей.  
В качестве источника данных мы используем **популярные Telegram-каналы по инвестициям**, затем индексируем сообщения с помощью [Faiss](https://github.com/facebookresearch/faiss) и формируем ответы с помощью языковой модели (например, [GigaChat](https://gigachat.ai/) и LangChain).

Основная цель проекта — **обеспечить быстрый доступ** к актуальным новостям из мира инвестиций, где пользователь может задать вопрос, а система найдёт релевантные сообщения и сгенерирует ответ, ссылаясь на конкретные источники.

---

## **Ключевые возможности**

1. **Сбор данных** из Telegram-каналов:
   - Поддержка **нескольких** инвестиционных каналов.
   - Фильтрация сообщений за последние *N* дней (по умолчанию 7) с помощью Telethon.
   - Работа с существующей сессией Telegram (не нужно авторизовываться каждый раз).

2. **Индексирование (Retrieval)**:
   - Использование [SentenceTransformer](https://www.sbert.net/) для эмбеддингов.
   - [Faiss](https://github.com/facebookresearch/faiss) для быстрого поиска релевантных сообщений.

3. **Генерация ответа (Augmented Generation)**:
   - Модель GigaChat (через LangChain) формирует ответ, используя найденные сообщения как контекст.
   - Автоматическая выдача ссылок на конкретные Telegram-сообщения, упомянутые в ответе.

4. **Пользовательский интерфейс (UI)**:
   - Web-интерфейс на базе [Streamlit](https://streamlit.io/).
   - Ползунок для настройки количества релевантных сообщений (top_k).
   - Отображение итогового ответа и краткого контекста со ссылками на источники.

5. **Деплой через ngrok** :
- временная ссылка по требованию

---

## **Структура репозитория**


### **tg_api.py**
Содержит функционал для:
- Подключения к Telegram API (через Telethon).
- Скачивания сообщений **только за последние N дней** (например, последние 7 дней).
- Сохранения их в `messages.json`.

### **index.py**
- Загружает `messages.json`.
- Генерирует эмбеддинги (SentenceTransformer).
- Создаёт Faiss-индекс для быстрого поиска (записывается в `faiss_index.bin`).
- Сохраняет таблицу сопоставления в `mapping.csv`.

### **llm.py**
- Загружает индекс и маппинг.
- Выполняет поиск *top_k* релевантных сообщений.
- Вызывает модель (GigaChat) для генерации ответа с учётом найденного контекста.
- Возвращает финальный ответ и контекст (тексты и ссылки на сообщения).

### **main.py**
- Web-приложение на [Streamlit](https://streamlit.io/):
  - Поле ввода запроса.
  - Кнопка/ползунок для настройки top_k.
  - Генерация ответа (вызывает `generate_response` из `llm.py`).
  - Отображение ответа и ссылок на исходные сообщения.

---

## **Источник данных: популярные инвестиционные каналы**
*(При желании вы можете указать свои каналы, либо добавить новые.)*

## **Авторы проекта**
Губин - создание mvp


Шевцов - корректировка с учетом обратной связи от ментора, развертывание через ngrok
