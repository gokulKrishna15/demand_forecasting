"""Ingest local vendor docs into Chroma vectorstore using sentence-transformers."""
from pathlib import Path
import os
import json

from backend.config import VECTORSTORE_DIR
from backend.data_adapter import docs_dir

DATA_DOCS = docs_dir() / 'sample_vendor_bids'
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)


def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = max(0, end - overlap)
    return chunks


def ingest():
    # lazy-import heavy dependencies so we can still run fallback ingestion when not installed
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print('sentence-transformers not available, continuing without embeddings:', e)
        model = None

    try:
        import chromadb
        from chromadb.config import Settings
        client = chromadb.Client(Settings(persist_directory=str(VECTORSTORE_DIR)))
        collection = client.get_or_create_collection('vendor_docs')
    except Exception as e:
        print('Chromadb not available or init failed:', e)
        collection = None

    docs = []
    for p in DATA_DOCS.glob('*'):
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            try:
                text = p.read_text(encoding='latin-1')
            except Exception:
                text = ''

        # If embeddings and chroma are available, chunk for better retrieval. Otherwise store full text.
        if collection and model is not None:
            try:
                chunks = chunk_text(text)
            except MemoryError:
                chunks = [text]
        else:
            chunks = [text]

        for i, c in enumerate(chunks):
            docs.append({'id': f"{p.name}_{i}", 'text': c, 'source': str(p.name)})

    if collection and model is not None:
        texts = [d['text'] for d in docs]
        embeddings = model.encode(texts, show_progress_bar=True)
        ids = [d['id'] for d in docs]
        metadatas = [{'source': d['source']} for d in docs]
        collection.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        client.persist()
        print(f'Ingested {len(docs)} chunks into chroma at {VECTORSTORE_DIR}')
    else:
        # fallback: write JSON file
        out = VECTORSTORE_DIR / 'vendor_docs.json'
        out.write_text(json.dumps(docs, indent=2))
        print('Saved chunks to', out)


if __name__ == '__main__':
    ingest()
