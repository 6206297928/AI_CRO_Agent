import os
import faiss
import numpy as np
import pandas as pd
import google.generativeai as genai

INDEX_FILE = "cro_memory.index"
META_FILE = "cro_memory.csv"

def embed(text, api_key):
    genai.configure(api_key=api_key)
    emb = genai.embed_content(
        model="models/embedding-001",
        content=text
    )
    return np.array(emb["embedding"]).astype("float32")

def load_index(dim):
    if os.path.exists(INDEX_FILE):
        return faiss.read_index(INDEX_FILE)
    return faiss.IndexFlatL2(dim)

def memory_agent(state: dict):
    api_key = state["api_key"]
    query = state.get("raw_cro_data", "")[:500]

    if not os.path.exists(INDEX_FILE):
        state["memory_text"] = "No past failed CRO ideas."
        return state

    vec = embed(query, api_key)
    index = load_index(len(vec))
    D, I = index.search(vec.reshape(1, -1), 3)

    meta = pd.read_csv(META_FILE)
    results = meta.iloc[I[0]]

    state["memory_text"] = results.to_string(index=False)
    return state

