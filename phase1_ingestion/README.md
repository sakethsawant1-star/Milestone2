# Phase 1: Data Ingestion & Knowledge Base Preparation

This directory will contain scripts and logic for:
- Fetching HTML content from the Groww URLs defined in Phase 0.
- Cleaning and parsing the HTML to extract factual data (e.g., expense ratio, NAV, exit load).
- Chunking the extracted text logically.
- Tagging chunks with metadata (source URL, last updated date).
- Setting up the vector database (e.g., ChromaDB or FAISS) and generating embeddings.
