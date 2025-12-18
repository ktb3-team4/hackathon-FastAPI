
## 엔드포인트 목록
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/fastapi/jobs` | 새로운 안부 메시지 생성 작업을 생성 |
| GET | `/fastapi//jobs/{job_id}` | 작업의 현재 상태를 조회 |
| GET | `/fastapi//jobs/{job_id}/result` | 작업의 결과를 조회 |



## 작업 상태 (status)

| 상태 | 설명 |
|------|------|
| `PENDING` | 작업이 큐에 대기 중 |
| `RUNNING` | 워커가 작업을 처리 중 |
| `DONE` | 작업이 성공적으로 완료됨 |
| `ERROR` | 작업 처리 중 오류 발생 |



## Error
422 Unprocessable Entity
- 필수 필드 누락
- 잘못된 데이터 타입
- Job Not Found



## /fastapi/jobs

input:
```json
{
  "name": "string (필수)",
  "relationName": "string (필수)",
  "chatStyleName": "string (필수)",
  "age": 25,
  "birthday": "string (선택)",
  "lastContactDate": "string (선택)",
  "interests": "string (선택)",
  "events": [
    {
      "date": "string (선택)",
      "description": "string (선택)"
    }
  ]
}
```

output:
```json
{
  "job_id": "string",
  "status": "string",
  "result": "string | null"
}
```
 

## /fastapi/jobs/{job_id}

input: none
output:
```json
{
  "job_id": "string",
  "status": "string",
  "result": "string | null"
}
```


## /fastapi/jobs/{job_id}/result

input: none
output:
```json
{
  "job_id": "string",
  "status": "string",
  "result": "string | null"
}
```




## test:
```bash
curl -X POST "http://localhost:8000/fastapi/jobs" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```




```bash
curl "http://localhost:8000/fastapi/jobs/{job_id}"
```



```bash
curl "http://localhost:8000/fastapi/jobs/{job_id}/result"
```