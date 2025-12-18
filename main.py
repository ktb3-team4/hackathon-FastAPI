from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok", "message": "Hello, World!"}


@app.get("/fastapi")
async def root():
    return {"status": "ok", "message": "Hello, World!"}
