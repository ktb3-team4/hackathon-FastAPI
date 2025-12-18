#app/worker.py
"""
백그라운드 워커

큐를 계속 감시하며 작업을 처리:
1. 큐에서 job_id 꺼내기
2. 상태를 RUNNING으로 변경
3. Ollama API 호출
4. 결과를 저장하고 상태를 DONE으로 변경
"""

import asyncio
from app.queue import job_queue
from app.store import store
from app.ollama import call_ollama


async def process_job():
    """백그라운드 워커 - 큐에서 job을 꺼내 처리"""
    print("🔄 워커 시작됨")
    while True:
        job_id = None
        try:
            job_id = await asyncio.to_thread(job_queue.get, timeout=1)
            print(f"📥 작업 수신: {job_id}")

            store[job_id]["status"] = "RUNNING"
            print(f"▶️  작업 시작: {job_id}")

            job_data = store[job_id]["data"]

            result = await call_ollama(job_data)
            print(f"✅ Ollama 응답 완료: {job_id}")

            store[job_id]["status"] = "DONE"
            store[job_id]["result"] = result

        except Exception as e:
            if job_id is not None:
                print(f"❌ 오류 발생: {job_id} - {e}")
                store[job_id]["status"] = "ERROR"
                store[job_id]["result"] = str(e)

        await asyncio.sleep(0.1)
