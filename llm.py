import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

import configparser

config = configparser.ConfigParser()
config.read('config.ini')
credentials = config['gigachat']['credentials']

llm = GigaChat(
    credentials=credentials,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
    streaming=False,
)

# Можно задать глобальные системные инструкции
system_prompt = SystemMessage(
    content=(
        "Ты бот-помощник, который отвечает на вопросы по новостной повестке. "
        "В ответах указывай, если известно, источник в виде ссылки. "
        "Если ответа нет, говори, что ты не знаешь. "
        "Важно: если используешь контекст, цитируй коротко и оставляй ссылку."
    )
)

def generate_response(
    query,
    model_name='all-MiniLM-L6-v2',
    index_file='faiss_index.bin',
    mapping_file='mapping.csv',
    top_k=3
):
    """
    Ищем топ-k релевантных сообщений с помощью FAISS и формируем ответ.
    """
    # Эмбеддинг запроса
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Загрузка индекса
    index = faiss.read_index(index_file)
    distances, indices = index.search(query_embedding, top_k)

    # Загрузка маппинга
    mapping = pd.read_csv(mapping_file)

    # Собираем список релевантных текстов
    relevant_texts = []
    for i in indices[0]:
        row = mapping.iloc[i]
        # Если хотим сформировать ссылку
        link = f"https://t.me/{row['channel']}/{row['id']}"
        text_snippet = row['text']
        relevant_texts.append((text_snippet, link))

    # Формируем контекст
    # Можно включить несколько текстов (top_k), но осторожно с длиной
    context_parts = []
    for idx, (txt, lnk) in enumerate(relevant_texts, start=1):
        context_parts.append(f"[Источник {idx}]: {txt[:500]}...\nСсылка: {lnk}")  
    context_str = "\n\n".join(context_parts)

    # Готовим prompt
    user_prompt = (
        f"Контекст:\n{context_str}\n\n"
        f"Вопрос: {query}\n"
        "Ответ:"
    )

    # Генерация ответа
    messages = [system_prompt, HumanMessage(content=user_prompt)]
    try:
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        answer = f"Ошибка генерации ответа: {e}"

    return answer, relevant_texts