#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color



echo -e "${GREEN}=== Ollama 서버 및 앱 시작 스크립트 ===${NC}\n"




# .env 파일 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ .env 파일 로드 완료${NC}"

else
    echo -e "${RED}✗ .env 파일을 찾을 수 없습니다${NC}"
    exit 1
fi




# 1. Ollama 설치 확인
echo -e "\n${YELLOW}[1/6] Ollama 설치 확인 중...${NC}"

if ! command -v ollama &> /dev/null; then
    echo -e "${RED}✗ Ollama가 설치되어 있지 않습니다${NC}"
    echo -e "${YELLOW}Ollama 설치 중...${NC}"


    # Linux용 Ollama 설치
    if [[ "$OSTYPE" == "darwin"* ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo -e "${RED}현재 OS는 자동 설치를 지원하지 않습니다${NC}"
        echo -e "${YELLOW}https://ollama.com 에서 수동으로 설치해주세요${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Ollama가 이미 설치되어 있습니다${NC}"
fi




# 2. Ollama 서비스 실행 확인
echo -e "\n${YELLOW}[2/6] Ollama 서비스 확인 중...${NC}"

if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Ollama 서비스 시작 중...${NC}"
    CUDA_VISIBLE_DEVICES=0 ollama serve &
    OLLAMA_PID=$!
    sleep 3
    echo -e "${GREEN}✓ Ollama 서비스 시작됨 (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${GREEN}✓ Ollama 서비스가 이미 실행 중입니다${NC}"
fi




# 3. Ollama 서버 응답 확인
echo -e "\n${YELLOW}[3/6] Ollama 서버 응답 확인 중...${NC}"

for i in {1..10}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama 서버가 정상 응답합니다${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}✗ Ollama 서버 응답 시간 초과${NC}"
        exit 1
    fi
    echo -e "${YELLOW}대기 중... ($i/10)${NC}"
    sleep 2
done



# 4. 모델 다운로드 확인
echo -e "\n${YELLOW}[4/6] 모델 다운로드 확인 중... (모델: $MODEL_NAME)${NC}"

if ! ollama list | grep -q "$MODEL_NAME"; then
    echo -e "${YELLOW}모델 다운로드 중... (시간이 걸릴 수 있습니다)${NC}"
    ollama pull "$MODEL_NAME"
    echo -e "${GREEN}✓ 모델 다운로드 완료${NC}"

else
    echo -e "${GREEN}✓ 모델이 이미 다운로드되어 있습니다${NC}"
fi




# 5. Python 의존성 확인
echo -e "\n${YELLOW}[5/6] Python 의존성 확인 중...${NC}"

if [ -f requirements.txt ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Python 의존성 설치 완료${NC}"
else
    echo -e "${YELLOW}! requirements.txt 파일이 없습니다${NC}"
fi




# 6. FastAPI 앱 실행
echo -e "\n${YELLOW}[6/6] FastAPI 앱 실행 중...${NC}"
echo -e "${GREEN}✓ 서버가 http://localhost:${PORT}/fastapi 에서 실행됩니다${NC}\n"

# .env 파일에서 ENV 변수 읽어오기 (기본값: production)
ENV=${ENV:-production}

if [ "$ENV" = "development" ]; then
    echo -e "${YELLOW}[개발 모드] --reload 활성화${NC}"
    echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요${NC}\n"
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload
else
    echo -e "${GREEN}[배포 모드] --reload 비활성화${NC}"
    echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요${NC}\n"
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
fi