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

# --- 3. THE MAIN ORCHESTRATION FUNCTION ---
def generate_response(cv_path: str, jd_text: str, history: List[Dict[str, str]]) -> str:
    try:
        # --- Step A: Load and Process Documents ---
        cv_text = load_document(cv_path)
        cv_chunks = chunk_text(cv_text)
        jd_chunks = chunk_text(jd_text)
        all_chunks = cv_chunks + jd_chunks
        
        # --- Step B: Build Retriever Index ---
        retriever = Retriever()
        retriever.build_index(all_chunks)
        
        # --- Step C: Retrieve Relevant Context ---
        last_user_message = next((msg['content'] for msg in reversed(history) if msg['role'] == 'user'), jd_text)
        context_chunks = retriever.search(query=last_user_message, k=3)
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
        # THIS IS THE CHANGED PART: We now use logging.error
        logging.error(f"An error occurred while generating a response: {e}", exc_info=True)
        return "Sorry, I encountered an error while generating a response. Please try again."