FROM --platform=linux/amd64 python:3.11-slim
WORKDIR /app

# 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

EXPOSE 8000

# FastAPI 실행 (app.main으로 수정!)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]