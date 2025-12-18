# app/prompt_builder.py
"""
프롬프트 생성 함수 모듈

XML 프롬프트 템플릿 파일에 사용자 데이터를 삽입하여 완성된 프롬프트를 생성합니다.
"""

import sys
from pathlib import Path
from typing import Dict
from app.config import USERPT, SYSTEMPT, SLLMPT



# 프로젝트 루트를 Python 경로에 추가 (스크립트로 실행될 때)
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))





def build_prompt(data: Dict) -> Dict[str, str]:
    """
    프롬프트 템플릿에 사용자 데이터를 삽입하여 완성된 프롬프트를 생성합니다.

    Args:
        name: 대상자 이름 (필수)
        relation_name: 관계명 (필수)
        chat_style_name: 채팅 스타일 (필수)
        age: 나이 (선택)
        birthday: 생일 (선택)
        last_contact_date: 마지막 연락일 (선택)
        interests: 관심사 및 취미 (선택)
        events: 최근 이벤트 목록 (선택)

    Returns:
        Dict[str, str]: {"system": 시스템 프롬프트, "user": 유저 프롬프트}
    """

    name = data["name"]
    relation_name = data["relationName"]
    chat_style_name = str(data["chatStyleName"])
    age = data.get("age")
    birthday = data.get("birthday")
    last_contact_date = data.get("lastContactDate")
    interests = data.get("interests")
    events = data.get("events")


    # 프롬프트 파일 경로 설정
    base_path = Path(__file__).parent.parent / "prompts"
    system_prompt_path = base_path / SYSTEMPT
    user_prompt_path = base_path / USERPT

    # 프롬프트 파일 읽기
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    with open(user_prompt_path, "r", encoding="utf-8") as f:
        user_prompt = f.read()

    # 시스템 프롬프트의 {{chatStyleName}} 치환
    system_prompt = system_prompt.replace("{{chatStyleName}}", chat_style_name)

    # 유저 프롬프트의 데이터 치환
    replacements = {
        "{{name}}": name,
        "{{relationName}}": relation_name,
        "{{chatStyleName}}": chat_style_name,
        "{{age}}": str(age) if age is not None else "정보 없음",
        "{{birthday}}": birthday if birthday else "정보 없음",
        "{{lastContactDate}}": last_contact_date if last_contact_date else "정보 없음",
        "{{interests}}": interests if interests else "정보 없음",
    }

    # events 포맷팅
    if events and len(events) > 0:
        events_text = "\n".join([
            f"   - {event.get('date', '날짜 미상')}: {event.get('description', '설명 없음')}"
            for event in events
        ])
    else:
        events_text = "정보 없음"

    replacements["{{events}}"] = events_text

    # 모든 플레이스홀더 치환
    for placeholder, value in replacements.items():
        user_prompt = user_prompt.replace(placeholder, value)

    return {
        "system": system_prompt,
        "user": user_prompt
    }





def build_prompt_sllm(data: Dict) -> str:
    """
    프롬프트 템플릿에 사용자 데이터를 삽입하여 완성된 프롬프트를 생성합니다.
    단, sLLM을 위한 간결한 프롬프트로 작성합니다.

    Args:
        name: 대상자 이름 (필수)
        relation_name: 관계명 (필수)
        chat_style_name: 채팅 스타일 (필수)
        age: 나이 (선택)
        birthday: 생일 (선택)
        last_contact_date: 마지막 연락일 (선택)
        interests: 관심사 및 취미 (선택)
        events: 최근 이벤트 목록 (선택)

    Returns:
        str: system + user 프롬프트
    """

    name = data["name"]
    relation_name = data["relationName"]
    chat_style_name = data["chatStyleName"]
    age = data.get("age")
    birthday = data.get("birthday")
    last_contact_date = data.get("lastContactDate")
    interests = data.get("interests")
    events = data.get("events")

    # 프롬프트 파일 경로 설정
    base_path = Path(__file__).parent.parent / "prompts"
    prompt_path = base_path / SLLMPT

    # 프롬프트 파일 읽기
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()


    # 프롬프트의 데이터 치환
    replacements = {
        "{{name}}": name,
        "{{relationName}}": relation_name,
        "{{chatStyleName}}": chat_style_name,
        "{{age}}": str(age) if age is not None else "정보 없음",
        "{{birthday}}": birthday if birthday else "정보 없음",
        "{{lastContactDate}}": last_contact_date if last_contact_date else "정보 없음",
        "{{interests}}": interests if interests else "정보 없음",
    }

    # events 포맷팅
    if events and len(events) > 0:
        events_text = "\n".join([
            f"   - {event.get('date', '날짜 미상')}: {event.get('description', '설명 없음')}"
            for event in events
        ])
    else:
        events_text = "정보 없음"


    replacements["{{events}}"] = events_text


    # 모든 플레이스홀더 치환
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)

    return prompt

"""
if __name__ == "__main__":
    print(build_prompt_sllm({
        "name": "홍길동",
        "relationName": "엄마",
        "chatStyleName": "편한 반말",
        "age": 25,
        "birthday": "1999-12-17",
        "lastContactDate": "2025-12-15",
        "interests": "축구, 영화 감상, 맛집 탐방",
        "events": [
        {
            "date": "2025-01-10",
            "description": "결혼기념일"
        }
        ]
    }))
    """