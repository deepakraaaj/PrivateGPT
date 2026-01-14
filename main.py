import os
import multiprocessing
from typing import List, Optional, Dict, Any, Union
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Model Configuration - Qwen 2.5 0.5B Instruct
REPO_ID = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
# Using Q8_0 for maximum accuracy while maintaining high speed on small models
FILENAME = "qwen2.5-0.5b-instruct-q8_0.gguf"
MODEL_DIR = "./models"

# Server Configuration
PORT = int(os.getenv("PORT", 8001))
HOST = os.getenv("HOST", "0.0.0.0")

# Inference Configuration
# Auto-detect CPU cores for threading
N_THREADS = max(1, multiprocessing.cpu_count())
CONTEXT_SIZE = 4096  # Qwen supports up to 32k, but 4k is safe for small RAM

# -----------------------------------------------------------------------------
# Model Loader
# -----------------------------------------------------------------------------
def load_model() -> Llama:
    """
    Downloads the model if not present and initializes the Llama engine.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, FILENAME)

    if not os.path.exists(model_path):
        print(f"📥 [System] Downloading model {FILENAME} from {REPO_ID}...")
        try:
            hf_hub_download(
                repo_id=REPO_ID,
                filename=FILENAME,
                local_dir=MODEL_DIR,
                local_dir_use_symlinks=False
            )
            print("✅ [System] Download complete.")
        except Exception as e:
            print(f"❌ [System] Failed to download model: {e}")
            raise RuntimeError(f"Could not download model: {e}")
    else:
        print(f"⚡ [System] Found cached model at {model_path}")

    print(f"⚙️ [System] Initializing Inference Engine with {N_THREADS} threads...")
    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=CONTEXT_SIZE,
            n_threads=N_THREADS,
            n_batch=512,        # Batch size for prompt processing
            verbose=False       # Reduce log noise
        )
        print("🚀 [System] Model Loaded Successfully!")
        return llm
    except Exception as e:
        print(f"❌ [System] Failed to initialize Llama: {e}")
        raise RuntimeError(f"Could not initialize model: {e}")

# Global LLM Instance
llm_instance: Optional[Llama] = None

# -----------------------------------------------------------------------------
# API Schemas (OpenAI Compatible)
# -----------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "qwen-0.5b"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = Field(default=None, description="Max tokens to generate")
    stream: bool = False

# -----------------------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------------------
app = FastAPI(title="FastQwenRunner", version="1.0.0")

@app.on_event("startup")
def startup_event():
    """Load model on startup to ensure readiness."""
    global llm_instance
    llm_instance = load_model()

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    if llm_instance:
        return {"status": "ok", "model": FILENAME}
    return JSONResponse(status_code=503, content={"status": "initializing"})

@app.get("/v1/models")
def list_models():
    """OpenAI-compatible models list."""
    return {
        "object": "list",
        "data": [
            {
                "id": FILENAME,
                "object": "model",
                "created": 1677610602,
                "owned_by": "self-hosted"
            }
        ]
    }

@app.post("/v1/chat/completions")
def create_chat_completion(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completion endpoint.
    """
    if not llm_instance:
        raise HTTPException(status_code=503, detail="Model is still loading")

    # Format messages for Llama
    messages_payload = [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        response = llm_instance.create_chat_completion(
            messages=messages_payload,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        return response
    except Exception as e:
        print(f"❌ [Error] Inference failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"🌍 [System] Starting Server on port {PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
