import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="School ERP Assistant", version="0.1.0")


def get_gemini_api_key() -> str | None:
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )

app.include_router(api_router)
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return (Path(__file__).resolve().parent / "frontend" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "gemini_key_configured": bool(get_gemini_api_key())}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
