from pathlib import Path
from backend.config import VECTORSTORE_DIR, DATA_DIR

def retrieve(query, k=5):
    try:
        import chromadb
        from chromadb.config import Settings
        client = chromadb.Client(Settings(persist_directory=str(VECTORSTORE_DIR)))
        collection = client.get_collection('vendor_docs')
        res = collection.query(query_texts=[query], n_results=k)
        docs = []
        for texts, metadatas, ids in zip(res['documents'], res['metadatas'], res['ids']):
            for t, m, _id in zip(texts, metadatas, ids):
                docs.append({'text': t, 'metadata': m, 'id': _id})
        return docs
    except Exception as e:
        # fallback to JSON file
        store = Path(VECTORSTORE_DIR) / 'vendor_docs.json'
        if store.exists():
            import json
            docs = json.loads(store.read_text())
            # naive text match
            hits = [d for d in docs if query.lower() in d['text'].lower()][:k]
            return hits
        print('Retrieve failed:', e)
        return []


if __name__ == '__main__':
    print(retrieve('warranty', k=3))
