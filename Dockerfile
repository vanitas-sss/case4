FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV INGEST_URL=http://backend:8000/api/v1/ingest
CMD python generator.py --url "$INGEST_URL" --interval 5
