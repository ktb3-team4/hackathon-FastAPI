#app/config.py
#환경변수 기본값

import os
import json
from pathlib import Path
from dotenv import load_dotenv



# .env 파일 로드
load_dotenv()



# 환경변수
PORT = os.getenv("PORT", 8000)
MODEL_NAME = os.getenv("MODEL_NAME", "llama2:13b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
TIMEOUT = float(os.getenv("TIMEOUT", "120.0"))
MODEL_SIZE = os.getenv("MODEL_SIZE", "medium")

PROMT_S = "prompt_for_system.txt"
PROMT_U = "prompt_for_user.txt"
if MODEL_SIZE == "small":
    PROMT_U = os.getenv("PROMPT_S", "prompt_for_small.txt")
elif MODEL_SIZE == "medium":
    PROMT_U = os.getenv("PROMPT_M", "prompt_for_medium.txt")
else:
    PROMT_S = os.getenv("PROMPT_LS", "prompt_for_system.txt")
    PROMT_U = os.getenv("PROMPT_LU", "prompt_for_user.txt")





# config.json 로드

CONFIG_PATH = Path(__file__).parent.parent / "config.json"



def load_ollama_options():
    """config.json에서 Ollama 옵션 로드"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("ollama_options", {})
        
    except FileNotFoundError:
        # 기본값 반환
        return {
            "num_predict": 100,
            "temperature": 0.6,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "frequency_penalty": 0.3,
            "stop": ["입력:", "출력:", "---" ],
        }





OLLAMA_OPTIONS = load_ollama_options()