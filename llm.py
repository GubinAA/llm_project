import pandas as pd
import configparser
import faiss
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from sentence_transformers import SentenceTransformer


# Загружаем конфигурацию из файла config.ini
config = configparser.ConfigParser()
config.read('config.ini')

credentials = config['gigachat']['credentials'] # Получаем credentials из файла config

# Авторизация в GigaChat
llm = GigaChat(
    credentials=credentials,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    # Отключает проверку наличия сертификатов НУЦ Минцифры
    verify_ssl_certs=False,
    streaming=False,
)

messages = [
    SystemMessage(
        content="Ты бот-помощник в ответе на вопросы про актуальной новостной повестке, \
        тебе будет приходить вопрос и контекст к нему, на которые надо отвечать. \
        Если ты не знаешь ответ на вопрос, то тебе не нужно его изобретать, \
        просто напиши что не знаешь"
    )
]

# Query Processing and RAG Integration

def generate_response(query, model_name='all-MiniLM-L6-v2',
                      index_file='faiss_index.bin',
                      mapping_file='mapping.csv'):
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Load FAISS index
    index = faiss.read_index(index_file)
    _, indices = index.search(query_embedding, 1)  # Retrieve top 1 results

    # Load mapping
    mapping = pd.read_csv(mapping_file)
    relevant_texts = [mapping.iloc[i]['text'] for i in indices[0]]

    # Combine relevant texts into a single context
    context = "\n\n".join(relevant_texts[:1])  # Use only top 1 texts to keep context manageable

    # Generate a response based on the context and query
    if relevant_texts:
        prompt = f"Контекст:\n{context}\n\nВопрос: {query}\nОтвет:"
        try:
            messages.append(HumanMessage(content=prompt))
            response = llm.invoke(messages)
        except Exception as e:
            response = f"Ошибка генерации ответа"
    else:
        response = "Извините, я не нашел релевантную информацию по вашему запросу. Попробуйте переформулировать запрос."

    return response, context