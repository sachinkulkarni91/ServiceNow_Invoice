from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.ai import router as ai_router
from .core.config import settings

app = FastAPI(title="ServiceNow AI Backend (OpenRouter)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)


@app.get("/healthz")
async def healthz():
    return {"ok": True}
