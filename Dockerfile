FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY app ./app
COPY prompts ./prompts
COPY config.json .env ./

EXPOSE 8000

# FastAPI 실행 (app.main:app로 수정)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

