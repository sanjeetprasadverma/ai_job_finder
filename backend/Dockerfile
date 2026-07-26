FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# COPY backend/ .

# COPY common/ ./common/

EXPOSE 8000

ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]