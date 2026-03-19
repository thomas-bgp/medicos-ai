import aiosqlite
from backend.config import settings


async def execute_query(sql: str) -> dict:
    """
    Executes a SELECT query against the SQLite database.
    Returns a dict with 'columns' and 'rows'.
    Raises ValueError if the query is not a SELECT or if execution fails.
    """
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        raise ValueError(
            "Apenas queries SELECT são permitidas. "
            f"Query recebida começava com: '{sql.strip()[:20]}'"
        )

    try:
        async with aiosqlite.connect(settings.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                return {
                    "columns": columns,
                    "rows": [dict(row) for row in rows],
                }
    except aiosqlite.Error as e:
        raise ValueError(f"Erro ao executar query no banco de dados: {e}") from e
