# HDFC Mutual Fund FAQ Assistant

An AI-powered, completely factual RAG (Retrieval-Augmented Generation) assistant designed to answer objective questions about HDFC Mutual Funds using Groww as the single source of truth.

## 🚀 Key Features
- **Zero Hallucination Guarantee:** Utilizes a strict Metadata Pre-Filtering strategy. Before searching for an answer, the AI routes the query to the exact mutual fund requested, preventing it from confusing NAVs or exit loads between funds.
- **Strict Compliance Guardrails:** A semantic gatekeeper intercepts all queries. If a user asks for investment advice or an unrelated question, it blocks the query and issues a standard, link-free refusal.
- **Automated Ingestion:** Uses GitHub Actions to scrape, clean, chunk, and embed the latest fund data directly into the Vector Database every single day at 2:00 AM UTC.
- **Modern Web Interface:** A lightweight, premium web interface served via a lightning-fast FastAPI backend.

## 🏗️ Supported Schemes
The assistant is explicitly locked to the following 6 HDFC mutual funds:
1. HDFC Mid-Cap Fund
2. HDFC Equity Fund (Flexi Cap)
3. HDFC Small Cap Fund
4. HDFC Large Cap Fund
5. HDFC Gold ETF Fund of Fund
6. HDFC Nifty 50 Index Fund

## ⚙️ Quick Start

### 1. Set up Environment
Create a `.env` file in the root directory and add your Google Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Install Dependencies
Make sure you are in your virtual environment and install the required packages:
```bash
pip install -r phase1_ingestion/requirements.txt
pip install -r phase2_rag/requirements.txt
pip install -r phase4_ui_api/requirements.txt
```

### 3. Start the Server
Run the FastAPI backend:
```bash
python -m uvicorn phase4_ui_api.api:app --reload
```
Once running, open your browser and navigate to: **http://localhost:8000**

## 🗺️ Project Architecture
See the full architectural phase breakdown in `docs/architecture.md`.

- **Phase 1 (Ingestion):** `scraper.py`, `cleaner.py`, `embedder.py` (ChromaDB + BAAI/bge-small-en-v1.5)
- **Phase 2 (RAG):** `rag_pipeline.py` (Query Routing, Metadata Filtering, Strict Prompts)
- **Phase 3 (Guardrails):** `guardrails.py` (Intent Classification, Refusal Handling)
- **Phase 4 (UI/API):** FastAPI Backend + Vanilla HTML/CSS Glassmorphic Chat UI
