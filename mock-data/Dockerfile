FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV INGEST_URL=http://backend:8000/api/v1/ingest
CMD ["python", "-u", "generator.py", "--interval", "5"]
