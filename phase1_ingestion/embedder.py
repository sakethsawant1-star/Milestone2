import os
import glob
import json
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_DIR = os.path.join(os.path.dirname(__file__), 'chunks')
DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')

def build_vector_db():
    print("Loading embedding model (BAAI/bge-small-en-v1.5)...")
    # Using the exact model proposed and approved
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    print("Initializing ChromaDB...")
    os.makedirs(DB_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_DIR)
    
    # Create or get the collection
    collection_name = "groww_mutual_funds"
    try:
        collection = client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Deleting and recreating for a fresh ingestion.")
        client.delete_collection(name=collection_name)
    except Exception:
        pass
        
    collection = client.create_collection(name=collection_name)
    
    json_files = glob.glob(os.path.join(CHUNKS_DIR, '*.json'))
    print(f"Found {len(json_files)} chunk files to embed.")
    
    total_inserted = 0
    
    for filepath in json_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
            
        if not chunks_data:
            continue
            
        # Extract fields for ChromaDB
        ids = [item['chunk_id'] for item in chunks_data]
        documents = [item['text'] for item in chunks_data]
        metadatas = [item['metadata'] for item in chunks_data]
        
        # Generate embeddings explicitly using our chosen model
        print(f"Generating embeddings for {len(documents)} chunks from {os.path.basename(filepath)}...")
        embeddings = model.encode(documents).tolist()
        
        # Insert into ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        total_inserted += len(documents)
        
    print(f"\nSuccessfully inserted {total_inserted} chunks into ChromaDB.")
    
    # --- Verification Test Query ---
    print("\n--- Running Verification Test Query ---")
    query_text = "What is the exit load?"
    query_embedding = model.encode([query_text]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )
    
    print(f"Query: '{query_text}'")
    if results['documents'] and len(results['documents'][0]) > 0:
        for i in range(len(results['documents'][0])):
            print(f"\nResult {i+1} Metadata: {results['metadatas'][0][i]}")
            print(f"Result {i+1} Text: {results['documents'][0][i]}")
            print(f"Distance: {results['distances'][0][i]}")
    else:
        print("No results found.")

if __name__ == '__main__':
    build_vector_db()
