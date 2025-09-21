FROM python:3.12.11-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential

# Copy requirements (if you have requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .env .env

# Copy your app code
COPY . .

# Expose FastAPI port
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "agentic_fastapi_app:app", "--host", "0.0.0.0", "--port", "8080"]