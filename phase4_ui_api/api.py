import sys
import os

# Ensure the root directory is in the path to import previous phases
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from phase2_rag.rag_pipeline import RAGPipeline
from phase3_guardrails.guardrails import IntentClassifier, safe_answer_query

app = FastAPI(title="Mutual Fund FAQ Assistant API")

# Initialize models
print("Initializing AI Pipeline and Guardrails...")
pipeline = RAGPipeline()
classifier = IntentClassifier(pipeline.groq_client)
print("Startup Complete!")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Pass the query through our strict guardrails and RAG pipeline
    answer = safe_answer_query(request.query, pipeline, classifier)
    return ChatResponse(response=answer)

# Mount the static directory to serve HTML, CSS, JS
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
