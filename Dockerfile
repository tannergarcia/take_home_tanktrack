FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && cd frontend && npm install && npm run build && rm -rf node_modules && apt-get purge -y nodejs npm && rm -rf /var/lib/apt/lists/*
CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:10000"]
