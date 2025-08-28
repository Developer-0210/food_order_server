FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements from project root
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from root into /app
COPY . .

# Run FastAPI with Gunicorn + Uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60"]
