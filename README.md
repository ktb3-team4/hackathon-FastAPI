### 개요
기획 목표: 가족/친구에게 자연스러운 안부 메시지를 AI로 생성하여, 사용자가 부담 없이 연락을 재개할 수 있도록 돕는 서비스




### Endpoints
| Method | Endpoint | Explanation |
|--------|-----------|------|
| POST | `/fastapi/jobs` | Create a new message creation task(job) and UUID |
| GET | `/fastapi//jobs/{job_id}` | Check the current status of the task |
| GET | `/fastapi//jobs/{job_id}/result` | Check the result of the task |


<details>
<summary><code>/fastapi/jobs</code></summary>                

**Input:**
```json
{
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
  ],
  "chatContent": "ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ  \n휴학하라고 하실거 같은데  \n고민했던 것들이나 궁금했던 것들  \n적어가봐  "
}
```

**Output:**
```json
{
  "job_id": "string",
  "status": "string",
  "result": "string | null"
}
```
</details>
 

<details>
<summary><code>/fastapi/jobs/{job_id}</code></summary>

**Input:** None

**Output:**
```json
{
  "job_id": "string",
  "status": "string",
  "result": "string | null"
}
```
</details>

<details>
<summary><code>/fastapi/jobs/{job_id}/result</code></summary>

**Input:** None

**Output:**
```json
{
  "job_id": "string",
  "status": "string",
  "result": "string | null"
}
```
</details>




### Status
| Status | Explanation |
|------|------|
| `PENDING` | The task(job) is waiting in the queue. |
| `RUNNING` | The worker is processing the task. |
| `DONE` | The task was successfully completed. |
| `ERROR` | An error occurred during task. |


### Error
422 Unprocessable Entity
- Required field missing
- Invalid data type
- Job Not Found



### Test:
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
  ],
  "chatContent": "ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ  \n휴학하라고 하실거 같은데  \n고민했던 것들이나 궁금했던 것들  \n적어가봐  "
}'
```

```bash
curl "http://localhost:8000/fastapi/jobs/{job_id}"
```

```bash
curl "http://localhost:8000/fastapi/jobs/{job_id}/result"
```
