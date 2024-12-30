import faiss
import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer

def load_messages(file_path='messages.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_faiss_index(
    messages,
    model_name='all-MiniLM-L6-v2',
    index_file='faiss_index.bin',
    mapping_file='mapping.csv'
):
    """
    Создаем FAISS-индекс по текстам, сохраняя метаданные в mapping.csv
    """
    model = SentenceTransformer(model_name)
    texts = [msg['text'] for msg in messages]
    embeddings = model.encode(texts, convert_to_numpy=True)

    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    faiss.write_index(index, index_file)

    # Cохраняем маппинг: здесь можно хранить и ссылку на сообщение
    df = pd.DataFrame(messages)
    # Если канал публичный, то ссылку на сообщение формируем как t.me/channel/<id> 
    # (или https://t.me/s/<channel>/<message_id> в случае, если канал не классического вида).
    # df['link'] = df.apply(lambda row: f"https://t.me/{row['channel']}/{row['id']}", axis=1)
    df.to_csv(mapping_file, index=False, encoding='utf-8')

    print(f"Indexed {len(texts)} messages into {index_file} with dimension {d}.")

if __name__ == '__main__':
    # Пример использования
    messages = load_messages('messages.json')
    build_faiss_index(messages)