from fastapi import APIRouter
from backend.schemas import ChatRequest, ChatResponse
from backend.services import sql_generator, response_generator
from backend import database

router = APIRouter(prefix="/api")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    message = request.message
    history = request.conversation_history

    # Step 1 — Generate SQL from the user's natural-language question
    try:
        sql = await sql_generator.generate_sql(message, history)
    except Exception as exc:
        return ChatResponse(
            response=(
                "Desculpe, não consegui entender sua pergunta. "
                "Pode reformulá-la de outra forma?"
            ),
            sql_query=None,
            results_count=None,
        )

    # Step 2 — Execute the generated SQL against the database
    try:
        results = await database.execute_query(sql)
    except ValueError as exc:
        return ChatResponse(
            response=(
                "Desculpe, não consegui buscar as informações solicitadas. "
                "Tente reformular sua pergunta com mais detalhes."
            ),
            sql_query=sql,
            results_count=None,
        )
    except Exception as exc:
        return ChatResponse(
            response=(
                "Ocorreu um erro ao acessar o banco de dados. "
                "Por favor, tente novamente em instantes."
            ),
            sql_query=sql,
            results_count=None,
        )

    # Step 3 — Generate a friendly natural-language response
    try:
        response_text = await response_generator.generate_response(
            message, results, sql, history
        )
    except Exception as exc:
        return ChatResponse(
            response=(
                "Encontrei os dados, mas ocorreu um erro ao formatar a resposta. "
                "Por favor, tente novamente."
            ),
            sql_query=sql,
            results_count=len(results.get("rows", [])),
        )

    return ChatResponse(
        response=response_text,
        sql_query=sql,
        results_count=len(results.get("rows", [])),
    )
