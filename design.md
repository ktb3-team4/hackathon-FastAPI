# 서비스 설계 문서

## 디자인

**질문: "왜 굳이 말투까지 반영해야 하는가?"**
```
우리 서비스의 핵심은 '단절된 관계를 자연스럽게 연결'하는 것입니다.
만약 몇 가지로 한정된 선택지만 제공한다면, 개인의 실제 말투나 구체적인 상황, 맥락을 담을 수 없겠죠.

그렇게 되면 "이것이 과연 진정한 의미의 연결인가?"라는 의문이 듭니다.

우리는 AI와 인간의 연결이 아니라, 인간과 인간의 연결을 도와주는 서비스를 만들고자 합니다. 

그렇기 때문에 개인의 말투, 관계의 특성, 과거 대화 내용 같은 사전정보가 반드시 반영되어야 합니다.
기존 대화 내용을 예시로 삼아서 말투를 추출하고, 실제 그 사람이 쓸 법한 메시지를 생성하는 거죠.
```


## 기술 스택
구체적 기술 스택
- GCP T4 GPU 인스턴스: 즉시 발급 가능, 무료 크레딧 활용
- Exaone3.5 (7.8B): LG AI Research 한국어 특화 모델
  - Llama2/Qwen 대비 한국어 출력 안정성 확보
  - T4 메모리 최적화 (10B 이상은 응답 지연 발생)



### model parameters
- `"num_predict": 80`: 단문 / 포맷 응답, 과도한 추론을 요구하지 않음, 설명형/복수 문단 아님. 짧은 한국어 2~3문장
- `"temperature": 0.6`: 너무 반복적인 형태를 출력하는 것을 방지하기 위해 0.5+ 설정
- `"top_p": 0.85` && `"top_k": 50`: sllm 특유의 "출력이 튀는 현상"을 방지, 단정한 문장 출력, 예측 가능한 어휘 반복 가능성 있으나 penalty도 함께 활용하여 방지
- `"repeat_penalty": 1.25`: 너무 반복되고 정형화된 출력을 방지하기 위해 일반적인 값보다 공격적으로 설정
- `"frequency_penalty": 0.3`: 의미 없는 단어 반복을 방지
- `"stop": ["입력:", "출력:", "예시", "---", "관계:"]`: Hallucination 차단 && 프롬프트를 그대로 반복하는 현상, 메타 메시지를 포함하는 경우를 방지


### 환경 설정
1. **GPU 환경이 필요**
- CPU 환경에서는 2~4GB 수준의 경량 모델만 사용 가능
- 이런 모델들은 긴 프롬프트를 처리하지 못하고 출력 품질도 떨어짐
- 우리는 '사용자 맞춤형 개인화 메시지'를 생성하기 위해 프롬프트에 관심사, 기념일, 기존 대화 내용 등 긴 컨텍스트를 담아야 함.
- 따라서 GPU 사용이 필수가 됨

2. **AWS가 아니라 GCP를 선택한 이유**
- AWS는 GPU 인스턴스 승인 후 발급까지 랜덤한 시간이 걸리는데, 며칠이 될 수도 있음
- 2~3일 해커톤에서는 매우 치명적임
- GCP는 GPU 인스턴스가 즉시 발급이 가능하고, 신규 유저 무료 크레딧도 활용할 수 있음



### 모델 선택: Exaone3.5 : 7.8B from LG AI Research

* [Hugging Face](https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct)
* [Ollama](https://ollama.com/library/exaone3.5:7.8b)

**1. 처음 시도:**
1. CPU 기반: qwen3:4b, llama3.2:3b, tinyllama:1.1b
2. GPU(T4) 기반: llama3.1:8b, llama2:13b, qwen3:8b, qwen3:13b
- 위 모델들은 한국어 특화가 아니다 보니 영어나 일본어, 중국어가 섞이는 문제가 계속 발생함. 프롬프트에 "한국어 사용"을 3번 이상 강조해도 반복 발생.
- 또한 한국어 문장이 매우 부자연스러웠음.

**2. 이후 시도:** exaone3.5:7.8b, exaone3.5:32b
- 한국어-영어 전용 모델이라 한국어로만 안정적으로 출력되고, 내용 품질도 확실히 좋았음
- 7.8B로 선택한 이유: T4 인스턴스에서 10B 이상 모델을 돌리면 메모리 문제로 응답 속도가 현저히 느려짐 (50~100초)
- 실시간성이 중요한 우리 서비스 특성상 7.8B가 최적이었음 (2~6초)



## 평가지표

### 1. 어떤 기술을 사용했는가?
#### Backend Core Stack
- FastAPI 0.109.0 - 비동기 웹 프레임워크 (최신 Python ASGI 기반)
- Uvicorn 0.27.0 - ASGI 웹 서버
- Pydantic 2.6.0+ - 데이터 검증 및 타입 안전성

#### AI/LLM 통합
- Ollama - 로컬 LLM 추론 엔진 (GPU 최적화)
- Exaone3.5:7.8b, llama2:13b, gemma2:2b 등 멀티 모델 지원
- httpx - 비동기 HTTP 클라이언트로 Ollama API 호출

#### 비동기 처리 아키텍처
- asyncio - Python 네이티브 비동기 런타임
- Queue - 인메모리 Job Queue 시스템
- Background Worker Pattern - startup 시점에 워커 태스크 시작

#### Infrastructure & DevOps
- Docker - 컨테이너화 (Linux amd64)
- GitHub Actions - CI/CD 파이프라인
- AWS EC2 - 프로덕션 배포 (SSH를 통한 자동 배포)
- GCP T4 server - GPU & 무료 크레딧 활용
- Docker Hub - 이미지 레지스트리

#### Testing & Quality Assurance
- pytest - 테스트 프레임워크
- pytest-asyncio - 비동기 테스트 지원




### 2. 어떤 구조로 설계했는가?
전체 아키텍처: Event-Driven + Async Job Queue
```
┌─────────────────────────────────────────────────────────────┐
│                    Client (HTTP Request)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  FastAPI (main.py)                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ POST /fastapi/jobs                                     │ │
│  │  1. UUID 생성 (8자리 short ID)                        │ │
│  │  2. Job을 store(dict)에 저장 (status: PENDING)        │ │
│  │  3. Job ID를 queue에 추가                             │ │
│  │  4. 즉시 job_id 반환 (Non-blocking)                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Background Worker (worker.py)                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Infinite Loop (asyncio.create_task)                    │ │
│  │  1. queue.get(timeout=1) - Job ID 꺼내기              │ │
│  │  2. status → RUNNING                                   │ │
│  │  3. call_ollama(job_data) 호출                        │ │
│  │  4. status → DONE, result 저장                        │ │
│  │  5. Exception → status: ERROR                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Ollama Integration (ollama.py)                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Prompt Builder 호출 (prompt_builder.py)            │ │
│  │    - 템플릿 파일 읽기 (prompts/mllm_prompt.txt)       │ │
│  │    - 플레이스홀더 치환 ({{name}}, {{relationName}})   │ │
│  │  2. httpx.AsyncClient.post()                           │ │
│  │    - URL: http://localhost:11434/api/generate          │ │
│  │    - Body: {model, prompt, options, keep_alive}        │ │
│  │  3. response.json()["response"] 반환                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Ollama (Local LLM Server)                                  │
│  - Model: llama2:13b / gemma2:2b                            │
│  - Options (config.json):                                   │
│    temperature: 0.5, top_p: 0.85, top_k: 40                 │
│    repeat_penalty: 1.4, num_predict: 80                     │
│    stop tokens: ["입력:", "예시", "---", "\n\n"]          │
└─────────────────────────────────────────────────────────────┘
```

#### 핵심 디자인 패턴
1. Producer-Consumer Pattern
    - Producer: POST /jobs 엔드포인트
    - Queue: queue.Queue() (인메모리)
    - Consumer: Background Worker (무한 루프)
2. Template Method Pattern
    - prompt_builder.py - build_prompt_llm() && build_prompt_sllm()
    - 템플릿 파일을 읽고 플레이스홀더를 데이터로 치환
3. Repository Pattern
    - store.py - Job 상태 관리 중앙화
    - queue.py - Queue 추상화
4. Dependency Injection
    - config.py - 환경 변수를 모듈로 import


### 3. 원하는 기획을 달성하기 위해 필요한 기술을 구현했는가?
기획 목표: 가족에게 자연스러운 안부 메시지를 AI로 생성하여, 사용자가 부담 없이 연락을 재개할 수 있도록 돕는 서비스

1. Chat Content 기반 Context-Aware Generation
- [main.py] `chatContent: Optional[str] = None`  # 기존 대화 기록
- [mllm_prompt.txt] 단순 템플릿이 아니라 대화 히스토리를 학습하여 자연스러운 연속성 제공
2. Stop Token Engineering
- [config.json] `"stop": ["입력:", "예시", "---", "관계:"]` → LLM이 프롬프트를 재출력하거나 메타 정보를 생성하는 것을 방지

3. Model-Specific Prompt Templates
- [prompt_for_llm.txt]: 14+B LLM용 (XML 포맷)
- [prompt_for_mllm.txt]: 8B~13B Small-LLM용 ([INST] 포맷)
- [prompt_for_sllm.txt]: 2B~4B Small-Small-LLM용
- 모델 크기에 따라 프롬프트 복잡도 조절




### 4. 해당 기술을 적절하게 사용했는가?
1. FastAPI의 Async/Await 활용
```
# main.py:52
async def create_job(request: JobRequest):
    # 동기 블로킹 없이 즉시 반환

# worker.py:18
async def process_job():
    # asyncio.to_thread로 동기 queue.get을 논블로킹으로 변환
    job_id = await asyncio.to_thread(job_queue.get, timeout=1)
```
평가: ✅ FastAPI의 비동기 특성을 최대한 활용


2. Background Task 패턴
```
# main.py:109-112
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_job())
```
평가: ✅ 서버 시작 시 워커를 자동으로 시작하여 별도 프로세스 관리 불필요


3. Pydantic Data Validation
```
# main.py:26-44
class Event(BaseModel):
    date: str
    description: str

class JobRequest(BaseModel):
    name: str
    relationName: str
    chatStyleName: str
    age: Optional[int] = None
```
평가: ✅ FastAPI + Pydantic으로 자동 검증 및 문서화


4. Template-Based Prompt Engineering
```
# prompt_builder.py:60-64
with open(system_prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 동적 치환
system_prompt = system_prompt.replace("{{chatStyleName}}", chat_style_name)
```
평가: ✅ 프롬프트를 코드에서 분리하여 유지보수성 향상



5. Ollama keep_alive=-1 최적화
```
# ollama.py:52
"keep_alive": -1  # 모델을 메모리에 계속 유지
```
평가: ✅ 매 요청마다 모델 로딩 시간 제거 (5-10초 절약)



### 5. 기술 적용에 창의성이 있는가?
1. Chat Content 기반 Tone Matching
    ```
    # JobRequest 모델에 chatContent 추가
    chatContent: Optional[str] = None
    ```
    - 창의성: 일반적인 템플릿 메시지가 아니라 이전 대화의 어조를 학습
    - 예: "ㅋㅋㅋㅋ 알겠어~" → AI도 "ㅋㅋ"를 자연스럽게 사용
    - 심리적 자연스러움 극대화 (로봇 같지 않은 메시지)


2. 프롬프트 내 우선순위 시스템
    - 프롬프트 내에서 정보 반영의 우선순위를 지정
    - 창의성: LLM에게 정보 중요도를 명시적으로 지시 - 가중치 프롬프팅
    - "나이"나 "관심사"보다 "관계"와 "말투"가 훨씬 중요하다는 도메인 지식 반영
    - Feature Engineering의 LLM 버전

3. Model-Agnostic Design
    ```
    # main.py:98-106
    @app.post("/model")
    async def change_model(request: ModelChangeRequest):
        config.MODEL_NAME = request.model_name
    ```
    - 창의성: Runtime에 모델 변경 가능 (서버 재시작 불필요)
    - A/B 테스트 또는 사용자별 모델 선택 가능
    - 모델 성능 비교 실험 가능

4. 로컬 LLM 활용
- OpenAI API 대신 Ollama 선택
- 비용 제로, 개인정보 보호, 네트워크 독립성
- 해커톤/스타트업 초기 단계에 최적

5. Job-Based Async Pattern
- 일반적인 동기 API: `POST /generate` → (30초 대기) → 응답
- 이 프로젝트: `POST /jobs` → 즉시 `job_id` 반환 → 폴링으로 결과 조회
- UX 개선: 사용자가 로딩 중에도 다른 작업 가능

6. Template Externalization
- 프롬프트를 코드에서 분리
- 비개발자(기획자)도 프롬프트 수정 가능
- 빠른 A/B 테스트 및 프롬프트 버전 관리






## Roadmap

### 기술 개선
- 완료된 Job 자동 만료 및 삭제
- Redis/PostgreSQL로 Job Store 교체 (영속성 확보)
- Retry 메커니즘 + 상세 에러 핸들링
- Prometheus 메트릭 + 구조화 로깅

### 기획
1. "이탈하는 시점이 언제죠?"
    - "3가지 critical moment가 있습니다: Day 1-3 (첫 경험), Day 7-14 (신기함 소진), Day 30+ (습관화 실패). 각 시점마다 다른 전략을 적용합니다."

2. "습관화 전략은요?"
    - "게임 디자인 원리를 차용했습니다: ① Variable Reward로 매번 다른 메시지 ② Contextual Trigger로 상황 기반 알림 ③ Progress Visualization으로 성취감 제공. 목표는 Day 30 Retention 40%입니다."

3. "대형 플랫폼 / 카카오가 베끼면요?"
    - "시간이 우리 편입니다: ① 6개월간 축적된 대화 데이터는 모방 불가 ② 빠른 의사결정으로 3개월에 6번 업데이트 ③ 니치 시장(100만 TAM) 장악 후 수직 통합 ④ 'AI 메신저'가 아닌 '디지털 효도' 브랜딩으로 정서적 충성도 확보. 카카오가 진입할 때는 이미 우리가 표준입니다."



#### 리텐션 전략 (2단계 방어선)
🎮 게임 디자인 원리 적용: "진행도 가시화 + 변동 보상"
##### **Level 1: Onboarding 최적화 (Day 0-3, 이탈률 40% → 15% 목표)**

1. **즉각적 성공 경험 설계**
```
기존: 가입 → 가족 등록 → 메시지 생성 → 전송 (4단계, 5분 소요)
개선: 가입 → 샘플 메시지 즉시 제공 → 전송 (2단계, 30초 소요)

Day 1: "엄마, 오늘 날씨가 춥네요. 따뜻하게 입고 나가세요!" (날씨 기반 자동 생성)
→ 가족 정보 입력 없이도 바로 전송 가능
```
2. **부모님 응답률 체크 및 대응**
```
if 48시간_내_응답_없음:
    # 대안 제시
    suggest_alternative = [
        "전화로 한번 연락해보시는 건 어떨까요?",
        "주말에 짧은 영상통화는 어떠세요?",
        "부모님이 자주 보시는 시간대(저녁 8시)에 다시 연락해볼까요?"
    ]
```
3. **Progress Indicator**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 따뜻한 자녀 레벨 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 첫 메시지 전송 완료 (Day 1)
⬜ 3일 연속 연락하기 (2/3)
⬜ 부모님 응답 받기 (0/1)
⬜ 전화 연결 1회 (0/1)

다음 레벨까지: 47%
```

##### **Level 2: 습관 형성 메커니즘 (Day 7-30, Retention 60% 목표)**
```
원리: BJ Fogg's Behavior Model (B = MAT)
Behavior = Motivation × Ability × Trigger
```

**구체적 실행:**

1. **Variable Reward (변동 보상) 시스템**
```
게임의 "랜덤 드롭" 개념 적용

고정 보상 (지루함):
- 매일 같은 시간, 같은 메시지

변동 보상 (기대감):
- Day 7: "어머니가 좋아하실 만한 레시피를 찾았어요!"
- Day 10: "아버지 생신이 2주 남았습니다. 선물 추천을 도와드릴까요?"
- Day 15: "최근 부모님 지역에 좋은 행사가 있어요!"
```

2. **Contextual Triggers (상황 기반 알림)**
```
// 단순 시간 알림 (X)
schedule.daily("09:00", sendNotification);

// 맥락 기반 트리거 (O)
if (weather.temp < 5 && parent.location === "outdoor_activity") {
    trigger: "어머니께서 산책 가시는 시간이네요. 따뜻한 메시지 어떠세요?"
}

if (stock_market.down > 3% && parent.interest === "investment") {
    trigger: "아버지께서 관심 있어 하시는 주식 시장이 변동이 있네요."
}

if (parent.birthday - today === 7) {
    trigger: "생신이 일주일 남았어요. 준비는 어떠세요?"
}
```


3. **Social Proof & Milestone**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 이번 주 통계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 나:          연락 5회 (평균보다 2회 많음!)
👥 두드림 사용자: 평균 3.2회
🏆 상위 30%:    연락 7회 이상

💬 부모님 응답률: 80% (↑15%)
❤️ 관계 점수:   87점 (지난주 대비 +12점)

🎁 연속 7일 달성! 
   "7일 연속 효자/효녀" 배지 획득
```

4. Message Variation Engine
```
# 메시지 다양성 보장 알고리즘
class MessageGenerator:
    def __init__(self):
        self.history = []  # 최근 30일 메시지 기록
        self.diversity_threshold = 0.7  # 유사도 70% 이상 시 재생성
    
    def generate(self, context):
        new_message = llm.generate(context)
        
        # 최근 메시지와 유사도 체크
        similarity = self.check_similarity(new_message, self.history[-7:])
        
        if similarity > self.diversity_threshold:
            # 다른 각도로 재생성
            new_message = llm.generate(
                context + f"이전 방식과 다른 {self.get_alternative_angle()}로 작성"
            )
        
        return new_message
    
    def get_alternative_angle(self):
        angles = [
            "유머러스한 톤",
            "구체적인 질문 포함",
            "추억 회상",
            "일상 공유",
            "감사 표현"
        ]
        return random.choice(angles)
```

---

##### **Level 3: 장기 충성도 확보 (Day 30+, Churn Rate <10% 목표)**

**1. Network Effect 구축**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
가족 네트워크 확장
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

현재: 나 → 엄마 (1:1)

확장: 나 ──→ 엄마
      ↓       ↗
      여동생 ─→ 아빠
      
- 가족 구성원 초대 시 메시지 크레딧 제공
- 가족 그룹 채팅방 자동 생성
- "이번 주 우리 가족 소통 순위: 3위/가족 4명"
```
**2. Data-Driven Personalization**
```
-- 사용자 행동 패턴 학습
SELECT 
    user_id,
    preferred_time,      -- 선호 연락 시간 (20:00-21:00)
    avg_message_length,  -- 평균 메시지 길이 (50자)
    response_rate,       -- 부모님 응답률 (75%)
    emotional_tone      -- 선호 톤 (따뜻함 > 유머)
FROM user_behavior_analytics
WHERE days_active > 30;

-- 시간이 지날수록 정확도 향상
-- Day 7:  정확도 60%
-- Day 30: 정확도 85%
-- Day 90: 정확도 95%
```

**3. Emotional Investment (감정적 투자)**
```
기능: "우리의 대화 기록"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 2024년 3월부터 함께한 지 180일

📊 통계:
- 총 메시지: 127개
- 전화 통화: 23회
- 부모님 미소 횟수: 84회 추정 😊

💝 가장 감동적이었던 메시지 Top 3:
1. "엄마 생신 축하해요!" (3/15)
2. "건강검진 결과 괜찮으셨다니 다행이에요" (5/23)
3. "명절 잘 보내셨어요?" (9/17)

🎬 추억 영상 만들기 (Beta)
→ AI가 대화 기록을 바탕으로 1분 영상 자동 생성
```

---

#### 대형 플랫폼 방어 전략
**핵심 전제: "카카오가 베끼면 어떻게 하나요?"**

##### **전략 1: Moat 구축 - 모방 불가능한 해자(垓子)**
```
┌─────────────────────────────────────────────────┐
│  대형 플랫폼은 "범용 기능"만 만들 수 있다      │
│  우리는 "초개인화 + 감정 데이터"에 집중        │
└─────────────────────────────────────────────────┘
```
**1. 축적된 대화 데이터 (Network Effect)**
```
# 카카오톡이 모방 시
카카오: 
    - 일반적 메시지 템플릿 제공
    - "안녕하세요, 날씨가 좋네요"
    
두드림 (6개월 후):
    - 180일간의 가족 대화 패턴 학습
    - "엄마, 어제 말씀하신 허리 통증은 좀 나아지셨어요? 
       병원 가보셨다고 하셨는데 결과 어떠셨어요?"
       
→ 데이터 축적 시간이 곧 경쟁력
→ 카카오가 따라올 때까지 최소 6개월 ~ 1년 선점 효과
```

**2. Vertical Integration (수직 계열화)**
```
범용 플랫폼의 한계:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
카카오톡: 메시징 (단일 기능)
           ↓
      연락만 가능

두드림 생태계:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
메시지 생성
    ↓
감정 분석
    ↓
행동 추천 (선물, 전화, 방문)
    ↓
가족 이벤트 관리
    ↓
건강/케어 서비스 연계 (Phase 4)
    ↓
지자체 돌봄 서비스 (B2G)

→ 단순 메시징을 넘어선 "관계 관리 플랫폼"
```

**3. Niche Market Dominance (니치 시장 장악)**
```
시장 세분화 전략:

카카오톡 (범용):
└─ 전체 사용자 (4,700만명)
    └─ 가족 소통 니즈 (1,000만명)
        └─ 부모님과 떨어져 사는 20-40대 (500만명)
            └─ 소통 부담을 느끼는 사용자 (300만명)
                └─ AI 활용에 긍정적 (100만명) ← 우리의 TAM

→ 100만 명 시장을 10% 점유 = 10만 MAU
→ 카카오 입장에서는 "너무 작은 시장"
→ 우리 입장에서는 "독점 가능한 시장"
```

---

##### **전략 2: Speed & Agility (속도와 민첩성)**
```
대형사 vs 스타트업 의사결정 속도

카카오가 기능 추가하는 과정:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
기획 (1개월) → 검토 (1개월) → 개발 (2개월) 
→ QA (1개월) → 법무 검토 (1개월) → 출시 (6개월)

두드림:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
아이디어 → 프로토타입 (1주) → AB 테스트 (1주) 
→ 배포 (1일) → 총 2주

→ 3개월 동안 우리는 6번 업데이트
→ 카카오는 0.5번 업데이트
```

**사례: 빠른 피봇 능력**
```
Week 1: 사용자 피드백 "메시지가 너무 형식적이에요"
Week 2: 프롬프트 수정 + AB 테스트 배포
Week 3: 만족도 65% → 82% 개선 확인
Week 4: 전체 적용

→ 대형사는 이런 속도로 못 움직임
```

---

##### **전략 3: Community & Brand (커뮤니티 충성도)**
```
기능은 베낄 수 있지만, 브랜드는 베낄 수 없다

"카카오톡의 가족 알림" (기능)
vs
"두드림" (효심 브랜드)

→ "나는 두드림으로 부모님과 소통해요"라는 정체성
→ 커뮤니티 형성: "이번 주 가장 감동적인 대화 공유" 이벤트
```

**구체적 브랜딩 전략:**

1. **Emotional Branding**
```
포지셔닝: "AI 메신저" (X) → "디지털 효도 동반자" (O)

스토리텔링:
"바쁜 당신을 대신해서, 
 AI가 부모님께 마음을 전해드립니다"

→ 광고: 딸이 출산 후 바빠서 연락 못하는데, 
        두드림이 자동으로 "엄마, 손주 사진 보내드려요" 전송
        → 할머니 감동
```

2. **User-Generated Content (UGC)**
```
인스타그램 해시태그 캠페인:
#두드림_효도챌린지
#부모님과의_대화

→ 사용자들이 자발적으로 브랜드 홍보
→ "카카오톡으로 하면 뭔가 특별하지 않잖아요"
```

3. **Mission-Driven Company**
```
"우리는 기술로 가족의 온기를 이어갑니다"

→ 수익의 1% 독거노인 돌봄 단체 기부
→ 매달 "이달의 효자/효녀" 선정 및 스토리 공유
→ 고령 부모님 무료 사용 지원

→ "카카오는 돈 벌려고 만든 거, 두드림은 진심"
```

---

##### **전략 4: Strategic Partnership (전략적 제휴)**
```
대형사가 모방할 쯤, 우리는 이미 생태계 구축 완료

제휴 타깃:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 통신사 (SKT, KT): 가족 결합 상품
2. 보험사 (삼성생명): 효도 보험 연계
3. 지자체: 독거노인 돌봄 서비스
4. 요양원: 가족-부모 소통 플랫폼
5. 선물 플랫폼 (카카오선물하기, 네이버 선물): 
   "어머니가 좋아하실 선물 추천"

→ 카카오가 진입할 때는 이미 우리가 표준(Standard)
```