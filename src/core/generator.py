import os
import logging # Import the logging module
import google.generativeai as genai
from typing import List, Dict

# Import our custom modules
from .loader import load_document
from .processor import chunk_text
from .retriever import Retriever

# --- 1. CONFIGURE THE GEMINI API ---
genai.configure(api_key=os.getenv("LLM_API_KEY"))

# --- 2. DEFINE THE PROMPT TEMPLATE ---
PROMPT_TEMPLATE = """
You are an expert technical hiring manager. Your goal is to conduct a realistic interview.
--- RULES ---
1. You MUST base every question strictly on the provided Job Description and Resume context.
2. Ask only one question at a time.
3. Do not ask generic questions like "What is your greatest weakness?".
4. After the user answers, you will provide brief, constructive feedback and then ask the next relevant question.
--- CONVERSATION HISTORY ---
{history}
--- CONTEXT FROM JOB DESCRIPTION ---
{jd_context}
--- CONTEXT FROM RESUME ---
{cv_context}
Based on the history and context, provide feedback on the last answer (if any) and ask the next single interview question.
"""

# --- 3. SINGLETON RETRIEVER ---
# The SentenceTransformer model is fairly slow to load. Creating a new
# Retriever() (and therefore a new model instance) on every single chat
# turn was the main latency bottleneck. We load the embedding model once
# at import time and simply rebuild the (cheap) FAISS index per request.
_retriever = Retriever()


# --- 4. THE MAIN ORCHESTRATION FUNCTION ---
def generate_response(cv_path: str, jd_text: str, history: List[Dict[str, str]]) -> str:
    try:
        # --- Step A: Load and Process Documents ---
        cv_text = load_document(cv_path)
        cv_chunks = chunk_text(cv_text)

        if not cv_chunks:
            return "Sorry, I couldn't extract any text from the uploaded resume. Please upload a text-based PDF/DOCX."

        # --- Step B: Build Retriever Index (resume only) ---
        # We only index the resume. The job description is short enough to
        # pass to the model in full, so retrieving JD chunks and mixing them
        # into "cv_context" (as the original code did) just duplicated the
        # JD text and mislabeled it as resume context.
        _retriever.build_index(cv_chunks)

        # --- Step C: Retrieve Relevant Resume Context ---
        last_user_message = next((msg['content'] for msg in reversed(history) if msg['role'] == 'user'), jd_text)
        context_chunks = _retriever.search(query=last_user_message, k=min(3, len(cv_chunks)))
        cv_context_str = "\n---\n".join(context_chunks)

        # --- Step D: Format History for Prompt ---
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

        # --- Step E: Engineer the Final Prompt ---
        final_prompt = PROMPT_TEMPLATE.format(
            history=history_str,
            jd_context=jd_text,
            cv_context=cv_context_str
        )

        # --- Step F: Call the Gemini API ---
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        response = model.generate_content(final_prompt)
        return response.text

    except Exception as e:
        logging.error(f"An error occurred while generating a response: {e}", exc_info=True)
        return "Sorry, I encountered an error while generating a response. Please try again."