#app/ollama.py
"""
Ollama API 호출
사용자 정보를 바탕으로 프롬프트를 생성하고
Ollama에 요청하여 AI 메시지를 받아옴
"""

import httpx
from app.config import MODEL_NAME, OLLAMA_URL, TIMEOUT, OLLAMA_OPTIONS
from app.prompt_builder import build_prompt, build_prompt_sllm



async def call_ollama(job_data: dict) -> str:
    """
    Ollama API를 호출하여 AI 메시지를 생성하는 함수

    Parameters:
    - job_data: 사용자 정보가 담긴 딕셔너리

    Returns:
    - AI가 생성한 안부 메시지 (문자열)
    """


    # 1. AI에게 전달할 프롬프트 생성
    """ for 20B+ model
    prompt = build_prompt(job_data)
    system_prompt = prompt["system"]
    user_prompt = prompt["user"]
    """

    prompt = build_prompt_sllm(job_data)



    # 2. HTTP 클라이언트 생성 (비동기)
    async with httpx.AsyncClient() as client:

        

        # 3. Ollama API에 POST 요청 보내기
        response = await client.post(
            OLLAMA_URL, # # Ollama 로컬 서버 주소

            # 요청 본문 (JSON 형식)
            json={
                "model": MODEL_NAME,      # 사용할 AI 모델 이름 (예: llama3)
                "prompt": prompt,         # 위에서 만든 프롬프트
                "stream": False,          # 스트리밍 안함 (전체 응답 한번에 받기)
                "options": OLLAMA_OPTIONS # config.json의 옵션 (temperature 등)
            },
            # 대기 (config.py에서 수정)
            timeout=TIMEOUT
        )




        # 4. HTTP 오류 발생 시 예외 발생시키기 (4xx, 5xx 에러)
        response.raise_for_status()


        # 5. 응답 JSON에서 "response" 필드 추출하여 반환
        return response.json()["response"]
    
 


#f
"""
사용자 정보:
- 이름: {job_data['name']}
- 관계: {job_data['relationName']}
- 대화 스타일: {job_data['chatStyleName']}
- 나이: {job_data['age']}
- 생일: {job_data['birthday']}
- 마지막 연락일: {job_data['lastContactDate']}
- 관심사: {job_data['interests']}

예정된 이벤트:
{chr(10).join([f"- {e['date']}: {e['description']}" for e in job_data['events']])}

위 정보를 바탕으로 안부 메시지를 작성해주세요.
"""