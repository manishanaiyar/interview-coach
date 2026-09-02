# --- Stage 1: The Builder (Optimized) ---
# This stage installs dependencies and cleans up in the same step.
# IMPORTANT: install the exact same sentence-transformers version used in
# requirements.txt, so the cache layout matches what the final image loads.
FROM python:3.10-slim AS builder

COPY requirements.txt .
RUN pip install --no-cache-dir $(grep -i '^sentence-transformers' requirements.txt) \
    && rm -rf /root/.cache/pip

# Modern sentence-transformers (>=2.3) stores models via the huggingface_hub
# cache, NOT the old ~/.cache/torch/sentence_transformers path. Download the
# model into that same cache layout so it can be copied verbatim below.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/model_cache')"


# --- Stage 2: The Final Image ---
# This is the small, efficient image we will actually deploy
FROM python:3.10-slim

WORKDIR /app

# Copy and install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Copy the application source code
COPY ./src ./src

# Copy the pre-downloaded model from the builder stage into the *huggingface
# hub* cache location, and point HF_HOME/SENTENCE_TRANSFORMERS_HOME at it so
# the app never tries to re-download the model at runtime.
COPY --from=builder /model_cache /root/.cache/huggingface_home
ENV HF_HOME=/root/.cache/huggingface_home
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface_home
ENV HF_HUB_OFFLINE=1

# Expose the port the FastAPI server will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]