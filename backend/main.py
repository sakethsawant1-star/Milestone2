import sys
import os
import traceback
from contextlib import asynccontextmanager

# Add root to path for importing phase modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

pipeline = None
classifier = None
startup_error = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the AI pipeline on startup."""
    global pipeline, classifier, startup_error
    try:
        print("Initializing RAG Pipeline and Guardrails...")
        from phase2_rag.rag_pipeline import RAGPipeline
        from phase3_guardrails.guardrails import IntentClassifier, safe_answer_query
        pipeline = RAGPipeline()
        classifier = IntentClassifier(pipeline.groq_client)
        print("Backend ready!")
    except Exception as e:
        startup_error = str(e)
        print(f"STARTUP ERROR: {e}")
        traceback.print_exc()
    yield


app = FastAPI(title="Groww Mutual Fund Assistant API", lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
async def health_check():
    if startup_error:
        return {"status": "error", "detail": startup_error}
    return {"status": "Groww Mutual Fund Assistant API is running"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if pipeline is None or classifier is None:
        raise HTTPException(
            status_code=503,
            detail=f"Backend not ready. Startup error: {startup_error}"
        )
    from phase3_guardrails.guardrails import safe_answer_query
    answer = safe_answer_query(request.query, pipeline, classifier)
    return ChatResponse(response=answer)

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
