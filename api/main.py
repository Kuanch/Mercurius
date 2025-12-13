from fastapi import FastAPI
from modules.sweeper.router import router as sweeper_router

app = FastAPI(title="Mercurius Platform")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(sweeper_router)
