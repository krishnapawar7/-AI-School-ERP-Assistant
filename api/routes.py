from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from utils.storage import append_history, read_history
from tools.attendance import AttendanceError, get_attendance_response
from tools.marks import MarksError, get_marks_response
from datetime import datetime
import uuid


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    student_id: Optional[str] = None
    tools: Optional[List[str]] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    intent: str
    plan: Any
    tool: Optional[List[str]]
    status: str
    response: Any


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")

    text = req.query.lower()
    tools = []
    if "attendance" in text:
        tools.append("attendance")
    if "mark" in text or "marks" in text:
        tools.append("marks")
    if "fee" in text or "fees" in text:
        tools.append("fees")
    if "homework" in text:
        tools.append("homework")
    if "timetable" in text or "class" in text:
        tools.append("timetable")

    intent = "Attendance" if "attendance" in text else (tools[0] if tools else "general")
    plan = {"steps": [f"Use {t} tool" for t in tools]} if tools else {"steps": ["Fallback: conversational response"]}

    try:
        if tools == ["attendance"]:
            response_text = get_attendance_response(req.student_id, req.query)
            status = "success"
        elif tools == ["marks"]:
            response_text = get_marks_response(req.student_id, req.query)
            status = "success"
        else:
            response_text = {"message": "Request accepted", "tools": tools}
            status = "ok"
    except (AttendanceError, MarksError) as exc:
        response_text = {"error": str(exc)}
        status = "error"
    except Exception as exc:  # pragma: no cover - defensive path
        response_text = {"error": "Unexpected exception"}
        status = "error"

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "query": req.query,
        "student_id": req.student_id,
        "intent": intent,
        "tools": tools,
        "response": response_text,
    }
    append_history(record)

    return ChatResponse(intent=intent, plan=plan, tool=tools, status=status, response=response_text)


@router.get("/chat/history")
async def chat_history(limit: int = 50):
    history = read_history()
    return {"status": "ok", "count": len(history), "history": history[-limit:]}
