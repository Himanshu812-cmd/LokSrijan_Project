from fastapi import FastAPI

from routers.challenges import router as challenge_router


app = FastAPI(
    title="Societal Challenge Platform",
    description="B1 Core API",
    version="1.0.0"
)


app.include_router(challenge_router)


@app.get("/")
def home():
    return {
        "message": "B1 Backend is running!"
    }