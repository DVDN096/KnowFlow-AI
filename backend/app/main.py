
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router


app = FastAPI(
    title="KnowFlow AI",
    description="Engineering Knowledge Intelligence Platform",
    version="1.0.0",
)


# CORS configuration for React frontend
# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "https://know-flow-ai-cyan.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(
    router,
    prefix="/api/v1",
    tags=["Knowledge Assistant"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to KnowFlow AI",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
