#app/main.py
"""
FastAPI 진입점

Endpoints:
- POST /fastapi/jobs: 새로운 작업 생성 (job_id 반환)
- GET /fastapi/jobs/{job_id}: 작업 상태 조회 (PENDING/RUNNING/DONE/ERROR)
- GET /fastapi/jobs/{job_id}/result: 작업 결과 조회
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import uuid
import asyncio

from app.store import store
from app.queue import job_queue
from app.worker import process_job
from app import config


app = FastAPI(root_path="/fastapi")


class Event(BaseModel):
    date: str
    description: str


class JobRequest(BaseModel):
    # 필수 필드
    name: str
    relationName: str
    chatStyleName: str

    # 선택 필드
    age: Optional[int] = None
    birthday: Optional[str] = None
    lastContactDate: Optional[str] = None
    interests: Optional[str] = None
    events: Optional[List[Event]] = None
    chatContent: Optional[str] = None


class ModelChangeRequest(BaseModel):
    model_name: str



@app.post("/jobs")
async def create_job(request: JobRequest):
    # 고유 ID 생성
    job_id = str(uuid.uuid4())[:8]

    # 저장소에 작업 저장
    store[job_id] = {
        "status": "PENDING",
        "data": request.model_dump(),
        "result": None
    }

    # 큐에 작업 추가
    job_queue.put(job_id)

    return {
        "job_id": job_id,
        "status": "PENDING"
    }



@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = store.get(job_id)
    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": job_id,
        "status": job["status"]
    }


@app.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    job = store.get(job_id)
    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job.get("result")
    }


@app.post("/model")
async def change_model(request: ModelChangeRequest):
    config.MODEL_NAME = request.model_name
    return {"model_name": config.MODEL_NAME}


@app.get("/model")
async def get_model():
    return {"model_name": config.MODEL_NAME}


@app.on_event("startup")
async def startup_event():
    # 백그라운드 워커 실행
    asyncio.create_task(process_job())
