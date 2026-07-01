import json
import os
import urllib.error
import urllib.request
from typing import Any

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta2"
GEMINI_DEFAULT_MODEL = "models/text-bison-001"


def get_gemini_api_key() -> str | None:
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )


def generate_gemini_text(prompt: str, model: str = GEMINI_DEFAULT_MODEL) -> str:
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("Gemini API key is not configured")

    url = f"{GEMINI_API_URL}/{model}:generateText?key={api_key}"
    payload = {
        "prompt": {"text": prompt},
        "temperature": 0.2,
        "maxOutputTokens": 250,
    }
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)
            candidates = result.get("candidates") or []
            if not candidates:
                raise ValueError("Gemini returned no output")
            return candidates[0].get("output", "").strip()
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"Gemini API request failed: {exc.code} {exc.reason}. {error_body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemini request error: {exc.reason}") from exc
    except ValueError as exc:
        raise
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc
