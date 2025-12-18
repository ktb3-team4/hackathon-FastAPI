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
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
TIMEOUT = float(os.getenv("TIMEOUT", "120.0"))





# 프롬프트 설정
SYSTEMPT = "xml_prompt_system.txt"
USERPT = "xml_prompt_user.txt"
SLLMPT = "sllm_prompt copy.txt"



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
            "temperature": 0.8,
            "top_p": 1.0,
            "top_k": 40,
            "num_predict": 200,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.2
        }



OLLAMA_OPTIONS = load_ollama_options()