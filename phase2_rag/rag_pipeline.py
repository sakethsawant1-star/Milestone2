import os
import sys
from dotenv import load_dotenv
import groq
import chromadb
from sentence_transformers import SentenceTransformer

# Fix Windows printing Unicode
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Constants
DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'phase1_ingestion', 'chroma_db')
COLLECTION_NAME = "groww_mutual_funds"

# List of known schemes
KNOWN_SCHEMES = [
    "HDFC Mid-Cap Fund",
    "HDFC Equity Fund (Flexi Cap)",
    "HDFC Small Cap Fund",
    "HDFC Large Cap Fund",
    "HDFC Gold ETF Fund of Fund",
    "HDFC Nifty 50 Index Fund"
]

class RAGPipeline:
    def __init__(self):
        # Initialize Groq Client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_key_here":
            raise ValueError("Invalid GROQ_API_KEY. Please set it in the .env file.")
        
        self.groq_client = groq.Groq(api_key=api_key)
        self.model_name = 'llama-3.3-70b-versatile'
        
        # Initialize Vector Database & Embedder
        print("Loading embedding model...")
        self.embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')
        
        print("Connecting to ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
        print("RAG Pipeline Initialized successfully.\n")

    def detect_scheme(self, query):
        """
        Uses Llama-3 to extract which mutual fund the user is asking about.
        Returns the exact string from KNOWN_SCHEMES, or None if no specific scheme is found.
        """
        prompt = f"""
        Given the following list of mutual funds:
        {KNOWN_SCHEMES}
        
        Which specific mutual fund is the user asking about in this query: "{query}"?
        If they are asking about one of the funds, reply with the EXACT name from the list.
        If it's a general question or doesn't match any, reply with "NONE".
        
        Reply with ONLY the exact name or "NONE". Do not provide any other text.
        """
        
        response = self.groq_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        if result in KNOWN_SCHEMES:
            return result
        return None

    def retrieve_context(self, query, scheme_name=None, k=3):
        """
        Retrieves the top-k most relevant chunks. Applies metadata pre-filtering if scheme_name is provided.
        """
        query_embedding = self.embedder.encode([query]).tolist()
        
        where_clause = None
        if scheme_name:
            where_clause = {"Scheme Name": scheme_name}
            
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=where_clause
        )
        
        chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                chunks.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
        return chunks

    def generate_answer(self, query, retrieved_chunks):
        """
        Generates the final response using strict prompt engineering with Llama-3.
        """
        if not retrieved_chunks:
            return "I'm sorry, I couldn't find any information about that in the official documentation."
            
        # Compile context
        context_str = "\n\n".join([f"Chunk {i+1}: {chunk['text']}" for i, chunk in enumerate(retrieved_chunks)])
        
        # We grab metadata from the very first (most relevant) chunk to construct the footer/citation.
        primary_metadata = retrieved_chunks[0]['metadata']
        source_url = primary_metadata['Source URL']
        scraped_date = primary_metadata['Scraped At'].split('T')[0] # just the YYYY-MM-DD
        
        # Strict Prompt Template
        prompt = f"""
        You are a factual AI assistant for HDFC Mutual Funds. 
        You must answer the user's query using ONLY the provided Context. 
        If the context does not contain the answer, say "I don't have enough information to answer that."
        
        CONSTRAINTS:
        1. Your answer must be absolutely factual, with zero financial advice or opinions.
        2. Your answer MUST be a maximum of 3 sentences. Do not exceed 3 sentences.
        3. Do not include any URLs or footers in your generated text. I will append those programmatically.
        
        Query: "{query}"
        
        Context:
        {context_str}
        
        Provide the answer below:
        """
        
        response = self.groq_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Enforce Constraints Programmatically
        final_response = f"{answer}\n\nCitation: {source_url}\nLast updated from sources: {scraped_date}"
        
        return final_response

    def answer_query(self, query):
        print(f"--- Processing Query: '{query}' ---")
        
        # Step 1: Detect Scheme
        scheme_name = self.detect_scheme(query)
        print(f"Detected Scheme: {scheme_name if scheme_name else 'None (Global Search)'}")
        
        # Step 2: Retrieve
        chunks = self.retrieve_context(query, scheme_name)
        print(f"Retrieved {len(chunks)} chunks.")
        
        # Step 3: Generate
        final_answer = self.generate_answer(query, chunks)
        print("\nFinal Answer:\n")
        print(final_answer)
        print("-" * 50 + "\n")
        
        return final_answer

if __name__ == "__main__":
    pipeline = RAGPipeline()
    
    # Test queries
    pipeline.answer_query("What is the minimum SIP for the HDFC Small Cap Fund?")
    pipeline.answer_query("What is the exit load for HDFC Flexi Cap?")
