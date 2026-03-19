from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []

class ChatResponse(BaseModel):
    response: str
    sql_query: str | None = None
    results_count: int | None = None
