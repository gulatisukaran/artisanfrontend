FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN  pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy all source code and .env file
COPY . .

# Ensure .env is present in the container
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:health_app", "--host", "0.0.0.0", "--port", "8080"]