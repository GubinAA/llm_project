#Preprocessing and Indexing
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import json

# Load messages
def load_messages(file_path='messages.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Prepare embeddings and build FAISS index
def build_faiss_index(messages, model_name='all-MiniLM-L6-v2', index_file='faiss_index.bin'):
    model = SentenceTransformer(model_name)
    texts = [msg['text'] for msg in messages]
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Create FAISS index
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    faiss.write_index(index, index_file)

    # Save mapping for retrieval
    mapping = pd.DataFrame(messages)
    mapping.to_csv('mapping.csv', index=False)
    print(f"Indexed {len(texts)} messages.")

# Uncomment to build the index once messages are fetched
messages = load_messages()
build_faiss_index(messages)