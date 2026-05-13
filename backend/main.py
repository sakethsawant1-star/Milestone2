import sys
import os

# Add root to path for importing phase modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from phase2_rag.rag_pipeline import RAGPipeline
from phase3_guardrails.guardrails import IntentClassifier, safe_answer_query

app = FastAPI(title="Groww Mutual Fund Assistant API")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow requests from the Vercel frontend. Replace with your actual Vercel URL
# after deploying the frontend (e.g. https://your-app.vercel.app).
# Use ["*"] for testing; restrict to your exact Vercel domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Update to your Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI pipeline on startup
print("Initializing RAG Pipeline and Guardrails...")
pipeline = RAGPipeline()
classifier = IntentClassifier(pipeline.groq_client)
print("Backend ready!")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
async def health_check():
    return {"status": "Groww Mutual Fund Assistant API is running"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer = safe_answer_query(request.query, pipeline, classifier)
    return ChatResponse(response=answer)
