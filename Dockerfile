# --- Stage 1: The Builder (Optimized) ---
# This stage installs dependencies and cleans up in the same step
FROM python:3.10-slim AS builder

# Install sentence-transformers and immediately clear the cache to save space
RUN pip install sentence-transformers && rm -rf /root/.cache/pip

# This command downloads the model into a specific folder
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

# Copy the pre-downloaded model from the builder stage
COPY --from=builder /model_cache /root/.cache/torch/sentence_transformers

# Expose the port the FastAPI server will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]