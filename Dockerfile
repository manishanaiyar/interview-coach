# 1. Base Image: Start with an official, lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy and install dependencies first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application's source code
COPY ./src ./src

# 5. Expose the port the FastAPI server will run on
EXPOSE 8000

# 6. Command to run the application when the container starts
# We use --host 0.0.0.0 to make the server accessible from outside the container
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]