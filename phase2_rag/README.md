# Phase 2: RAG Pipeline Development

This directory will contain the core retrieval and generation logic:
- Connecting to the vector database to perform similarity search based on query embeddings.
- Implementing the strict prompt template enforcing constraints (max 3 sentences, 1 citation link, date footer).
- Connecting to the LLM for response generation.
