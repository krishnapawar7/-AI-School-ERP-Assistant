from fastapi import APIRouter, HTTPException

from agents.executor import executor
from agents.memory import memory
from agents.planner import planner
from models.request import ChatRequest
from models.response import APIError, ChatResponse, HistoryResponse, LogsResponse
from utils.gemini import generate_gemini_text, get_gemini_api_key
from utils.logger import logger
from utils.storage import append_history, read_history
from datetime import datetime
import json
import uuid

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")

    resolved_query = memory.resolve_followup(req.session_id, req.query)
    memory.add_message(req.session_id, "user", req.query)

    plan = planner.plan(resolved_query)
    student_id = req.student_id or plan.entities.get("student_id")

    if not student_id:
        return ChatResponse(
            intent="Attendance",
            confidence=plan.confidence,
            plan=plan.tools,
            entities=plan.entities,
            tool=plan.tools,
            status="error",
            response={"error": "Invalid student ID"},
            errors=[APIError(tool=tool_name, error="Invalid student ID") for tool_name in plan.tools],
        )

    execution = executor.execute(student_id, resolved_query, plan.tools)
    enable_gemini = req.use_gemini
    results = execution["results"]
    errors = []
    for name in execution.get("errors", []):
        if ":" in name:
            tool_name, error_message = name.split(":", 1)
            errors.append(APIError(tool=tool_name, error=error_message))
        else:
            errors.append(APIError(tool=name, error="unknown"))

    if plan.tools == ["attendance"] and execution["status"] == "success":
        response_payload = results.get("attendance", results)
    elif plan.tools == ["marks"] and execution["status"] == "success":
        response_payload = results.get("marks", results)
    else:
        response_payload = results

    if enable_gemini:
        try:
            prompt = (
                f"A school ERP assistant should answer the user query using the following tool results:\n"
                f"User query: {resolved_query}\n"
                f"Tool results: {json.dumps(results, ensure_ascii=False)}\n"
                "Provide a concise, helpful answer based on that data."
            )
            gemini_output = generate_gemini_text(prompt)
            if isinstance(response_payload, dict):
                response_payload["gemini_output"] = gemini_output
            else:
                response_payload = {"result": response_payload, "gemini_output": gemini_output}
        except Exception as exc:
            errors.append(APIError(tool="gemini", error=str(exc)))

    memory.add_message(req.session_id, "assistant", str(results))
    logger.log(req.session_id, req.query, plan.intent, plan.tools, results, 0.0, execution["status"], execution["errors"])

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "query": req.query,
        "student_id": student_id,
        "intent": plan.intent,
        "tools": plan.tools,
        "response": results,
    }
    append_history(record)

    return ChatResponse(
        intent=plan.intent.capitalize(),
        confidence=plan.confidence,
        plan=plan.tools,
        entities=plan.entities,
        tool=plan.tools,
        status=execution["status"],
        response=response_payload,
        errors=errors,
    )


@router.get("/chat/history")
async def chat_history(limit: int = 50):
    history = read_history()
    return {"status": "ok", "count": len(history), "history": history[-limit:]}


@router.get("/chat/history/{session_id}", response_model=HistoryResponse)
def get_history(session_id: str):
    history = memory.history(session_id)
    return HistoryResponse(session_id=session_id, history=history)


@router.get("/logs", response_model=LogsResponse)
def get_logs():
    return LogsResponse(logs=logger.history())
