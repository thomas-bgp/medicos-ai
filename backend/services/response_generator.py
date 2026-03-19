import json
import anthropic
from backend.config import settings

_SYSTEM_PROMPT = """Você é um assistente amigável que ajuda pacientes a encontrar médicos de confiança no Brasil.

Diretrizes de resposta:
- Responda de forma conversacional e útil em português.
- Use bullet points para listar médicos.
- Sempre mencione nota, especialidade, cidade e hospital quando disponível.
- Se não houver resultados, sugira reformular a pergunta.
- Se o paciente perguntar se um médico é de confiança, baseie-se na nota média e nos comentários.
- Seja honesto sobre as notas:
    • Nota acima de 4.5 = excelente
    • Nota entre 4.0 e 4.5 = muito bom
    • Nota entre 3.5 e 4.0 = bom
    • Nota abaixo de 3.5 = atenção — considere outras opções
- Nunca invente informações que não estejam nos dados fornecidos.
- Seja empático: lembre-se que o paciente pode estar preocupado com a saúde.
"""


async def generate_response(
    message: str,
    query_results: dict,
    sql_query: str,
    conversation_history: list[dict],
) -> str:
    """
    Uses Claude Haiku to generate a friendly Portuguese response based on
    the original question and the SQL query results.
    """
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    results_json = json.dumps(query_results, ensure_ascii=False, indent=2)
    rows_count = len(query_results.get("rows", []))

    user_content = (
        f"Pergunta do paciente: {message}\n\n"
        f"Query SQL executada:\n{sql_query}\n\n"
        f"Resultados encontrados ({rows_count} registro(s)):\n{results_json}"
    )

    # Build context from the last 5 turns of history
    context_messages: list[dict] = []
    for turn in conversation_history[-5:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            context_messages.append({"role": role, "content": content})

    context_messages.append({"role": "user", "content": user_content})

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=context_messages,
    )

    return response.content[0].text.strip()
