import tempfile
import os
import json
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv # <-- 1. IMPORT load_dotenv

load_dotenv() # <-- 2. CALL load_dotenv TO LOAD THE .env FILE

if not os.getenv("LLM_API_KEY"):
    logging.warning(
        "LLM_API_KEY is not set. Create a .env file with LLM_API_KEY=<your-gemini-key> "
        "or the /chat endpoint will fail on every request."
    )

# Import our core RAG function from the generator module
from ..core.generator import generate_response

# --- PYDANTIC MODELS ---
class ChatResponse(BaseModel):
    response: str

# --- FASTAPI APP ---
app = FastAPI(
    title="Contextual Interview Coach API",
    description="API for the Contextual Interview Coach powered by Gemini and RAG.",
    version="1.0.0"
)

# --- CHAT ENDPOINT ---
@app.post("/chat", response_model=ChatResponse)
async def handle_chat(
    cv_file: UploadFile = File(...),
    jd_text: str = Form(...),
    history_str: str = Form(...)
):
    temp_cv_path = None
    try:
        # Use only the file extension for the suffix, not the whole
        # (user-controlled) filename.
        suffix = Path(cv_file.filename or "").suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await cv_file.read())
            temp_cv_path = tmp.name

        history = json.loads(history_str)

        # generate_response() is a synchronous, CPU/IO-heavy function
        # (embedding model, FAISS index build, Gemini API call). Calling it
        # directly inside this async endpoint would block the event loop
        # and stall every other in-flight request. Run it in a worker
        # thread instead.
        ai_response = await run_in_threadpool(
            generate_response,
            cv_path=temp_cv_path,
            jd_text=jd_text,
            history=history
        )
        return ChatResponse(response=ai_response)

    except Exception as e:
        logging.error(f"Error in /chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
    
    finally:
        if temp_cv_path and os.path.exists(temp_cv_path):
            os.remove(temp_cv_path)