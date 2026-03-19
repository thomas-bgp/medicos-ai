"""
Browse router — rotas de navegação estruturada do diretório de médicos.
Todas as rotas consultam o banco SQLite diretamente via aiosqlite.
"""

import re
import unicodedata

import aiosqlite
from fastapi import APIRouter, HTTPException, Query

from backend.config import settings
from backend.schemas import (
    Avaliacao,
    EspecialidadeDetalheResponse,
    EspecialidadeItem,
    EspecialidadesResponse,
    HospitalDetalheResponse,
    HospitalItem,
    HospitaisResponse,
    MedicoPerfilResponse,
    MedicoResumo,
    Procedimento,
    SearchResponse,
    StatsResponse,
)

router = APIRouter(prefix="/api")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """
    Converte um texto para slug ASCII em caixa-baixa com hífens.
    Ex.: "Ortopedia e Traumatologia" -> "ortopedia-e-traumatologia"
         "Ginecologia e Obstetrícia" -> "ginecologia-e-obstetricia"
         "Hospital Moinhos de Vento" -> "hospital-moinhos-de-vento"
    """
    # Normaliza para NFD e remove os diacríticos (acentos)
    nfd = unicodedata.normalize("NFD", text)
    ascii_text = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    # Caixa baixa e substitui qualquer sequência de não-alfanuméricos por hífen
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug


async def _fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    """Executa uma query SELECT e retorna lista de dicts."""
    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def _fetch_one(sql: str, params: tuple = ()) -> dict | None:
    """Executa uma query SELECT e retorna o primeiro resultado ou None."""
    rows = await _fetch_all(sql, params)
    return rows[0] if rows else None


def _sort_clause(sort: str, table_alias: str = "m") -> str:
    """Retorna a cláusula ORDER BY de acordo com o parâmetro sort."""
    if sort == "experiencia":
        return f"{table_alias}.anos_experiencia DESC NULLS LAST"
    if sort == "avaliacoes":
        return f"{table_alias}.total_avaliacoes DESC"
    # padrão: nota
    return f"{table_alias}.nota_media DESC, {table_alias}.total_avaliacoes DESC"


def _row_to_medico_resumo(row: dict) -> MedicoResumo:
    return MedicoResumo(
        id=row["id"],
        nome=row["nome"],
        crm=row["crm"],
        subespecialidade=row.get("subespecialidade"),
        hospital_principal=row.get("hospital_principal"),
        nota_media=row.get("nota_media") or 0.0,
        total_avaliacoes=row.get("total_avaliacoes") or 0,
        anos_experiencia=row.get("anos_experiencia"),
        valor_consulta=row.get("valor_consulta"),
    )


# ---------------------------------------------------------------------------
# GET /api/especialidades
# ---------------------------------------------------------------------------

@router.get("/especialidades", response_model=EspecialidadesResponse)
async def listar_especialidades() -> EspecialidadesResponse:
    """Lista todas as especialidades com contagem de médicos."""
    rows = await _fetch_all(
        """
        SELECT especialidade, COUNT(*) AS count
        FROM medicos m
        WHERE m.cidade = 'Porto Alegre'
        GROUP BY m.especialidade
        ORDER BY m.especialidade
        """
    )
    items = [
        EspecialidadeItem(
            especialidade=row["especialidade"],
            count=row["count"],
            slug=_slugify(row["especialidade"]),
        )
        for row in rows
    ]
    return EspecialidadesResponse(especialidades=items)


# ---------------------------------------------------------------------------
# GET /api/especialidades/{slug}
# ---------------------------------------------------------------------------

@router.get("/especialidades/{slug}", response_model=EspecialidadeDetalheResponse)
async def detalhe_especialidade(
    slug: str,
    sort: str = Query(default="nota", pattern="^(nota|experiencia|avaliacoes)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> EspecialidadeDetalheResponse:
    """Lista médicos de uma especialidade a partir do slug."""
    # Descobre o nome real da especialidade pelo slug
    all_esp = await _fetch_all(
        "SELECT DISTINCT especialidade FROM medicos WHERE cidade = 'Porto Alegre'"
    )
    especialidade_nome: str | None = None
    for row in all_esp:
        if _slugify(row["especialidade"]) == slug:
            especialidade_nome = row["especialidade"]
            break

    if especialidade_nome is None:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada.")

    order = _sort_clause(sort)
    offset = (page - 1) * limit

    count_row = await _fetch_one(
        "SELECT COUNT(*) AS total FROM medicos m WHERE m.especialidade = ? AND m.cidade = 'Porto Alegre'",
        (especialidade_nome,),
    )
    total = count_row["total"] if count_row else 0

    rows = await _fetch_all(
        f"""
        SELECT m.id, m.nome, m.crm, m.subespecialidade, m.hospital_principal,
               m.nota_media, m.total_avaliacoes, m.anos_experiencia, m.valor_consulta
        FROM medicos m
        WHERE m.especialidade = ? AND m.cidade = 'Porto Alegre'
        ORDER BY {order}
        LIMIT ? OFFSET ?
        """,
        (especialidade_nome, limit, offset),
    )

    return EspecialidadeDetalheResponse(
        especialidade=especialidade_nome,
        total=total,
        medicos=[_row_to_medico_resumo(r) for r in rows],
    )


# ---------------------------------------------------------------------------
# GET /api/hospitais
# ---------------------------------------------------------------------------

@router.get("/hospitais", response_model=HospitaisResponse)
async def listar_hospitais() -> HospitaisResponse:
    """Lista todos os hospitais com contagem de médicos."""
    # Tenta usar a tabela medico_hospitais quando existir; caso contrário usa
    # hospital_principal na tabela medicos como fallback.
    try:
        rows = await _fetch_all(
            """
            SELECT mh.hospital_nome AS hospital, COUNT(DISTINCT mh.medico_id) AS count
            FROM medico_hospitais mh
            JOIN medicos m ON m.id = mh.medico_id
            WHERE m.cidade = 'Porto Alegre'
            GROUP BY mh.hospital_nome
            ORDER BY mh.hospital_nome
            """
        )
        if not rows:
            raise ValueError("tabela vazia")
    except Exception:
        rows = await _fetch_all(
            """
            SELECT m.hospital_principal AS hospital, COUNT(*) AS count
            FROM medicos m
            WHERE m.cidade = 'Porto Alegre'
              AND m.hospital_principal IS NOT NULL
              AND m.hospital_principal != ''
            GROUP BY m.hospital_principal
            ORDER BY m.hospital_principal
            """
        )

    items = [
        HospitalItem(
            hospital=row["hospital"],
            count=row["count"],
            slug=_slugify(row["hospital"]),
        )
        for row in rows
    ]
    return HospitaisResponse(hospitais=items)


# ---------------------------------------------------------------------------
# GET /api/hospitais/{slug}
# ---------------------------------------------------------------------------

@router.get("/hospitais/{slug}", response_model=HospitalDetalheResponse)
async def detalhe_hospital(
    slug: str,
    sort: str = Query(default="nota", pattern="^(nota|experiencia|avaliacoes)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> HospitalDetalheResponse:
    """Lista médicos de um hospital a partir do slug."""
    # Descobre o nome real do hospital
    try:
        all_hosp = await _fetch_all(
            """
            SELECT DISTINCT mh.hospital_nome AS hospital
            FROM medico_hospitais mh
            JOIN medicos m ON m.id = mh.medico_id
            WHERE m.cidade = 'Porto Alegre'
            """
        )
        if not all_hosp:
            raise ValueError("tabela vazia")
    except Exception:
        all_hosp = await _fetch_all(
            """
            SELECT DISTINCT m.hospital_principal AS hospital
            FROM medicos m
            WHERE m.cidade = 'Porto Alegre'
              AND m.hospital_principal IS NOT NULL
              AND m.hospital_principal != ''
            """
        )

    hospital_nome: str | None = None
    for row in all_hosp:
        if _slugify(row["hospital"]) == slug:
            hospital_nome = row["hospital"]
            break

    if hospital_nome is None:
        raise HTTPException(status_code=404, detail="Hospital não encontrado.")

    order = _sort_clause(sort)
    offset = (page - 1) * limit

    # Tenta via medico_hospitais, cai para hospital_principal
    try:
        count_row = await _fetch_one(
            """
            SELECT COUNT(DISTINCT m.id) AS total
            FROM medicos m
            JOIN medico_hospitais mh ON mh.medico_id = m.id
            WHERE mh.hospital_nome = ? AND m.cidade = 'Porto Alegre'
            """,
            (hospital_nome,),
        )
        total = count_row["total"] if count_row else 0

        rows = await _fetch_all(
            f"""
            SELECT DISTINCT m.id, m.nome, m.crm, m.subespecialidade, m.hospital_principal,
                   m.nota_media, m.total_avaliacoes, m.anos_experiencia, m.valor_consulta
            FROM medicos m
            JOIN medico_hospitais mh ON mh.medico_id = m.id
            WHERE mh.hospital_nome = ? AND m.cidade = 'Porto Alegre'
            ORDER BY {order}
            LIMIT ? OFFSET ?
            """,
            (hospital_nome, limit, offset),
        )
    except Exception:
        count_row = await _fetch_one(
            "SELECT COUNT(*) AS total FROM medicos m WHERE m.hospital_principal = ? AND m.cidade = 'Porto Alegre'",
            (hospital_nome,),
        )
        total = count_row["total"] if count_row else 0

        rows = await _fetch_all(
            f"""
            SELECT m.id, m.nome, m.crm, m.subespecialidade, m.hospital_principal,
                   m.nota_media, m.total_avaliacoes, m.anos_experiencia, m.valor_consulta
            FROM medicos m
            WHERE m.hospital_principal = ? AND m.cidade = 'Porto Alegre'
            ORDER BY {order}
            LIMIT ? OFFSET ?
            """,
            (hospital_nome, limit, offset),
        )

    return HospitalDetalheResponse(
        hospital=hospital_nome,
        total=total,
        medicos=[_row_to_medico_resumo(r) for r in rows],
    )


# ---------------------------------------------------------------------------
# GET /api/medicos/{id}
# ---------------------------------------------------------------------------

@router.get("/medicos/{medico_id}", response_model=MedicoPerfilResponse)
async def perfil_medico(medico_id: int) -> MedicoPerfilResponse:
    """Retorna o perfil completo de um médico."""
    medico = await _fetch_one(
        """
        SELECT m.id, m.nome, m.crm, m.especialidade, m.subespecialidade,
               m.hospital_principal, m.nota_media, m.total_avaliacoes,
               m.anos_experiencia, m.valor_consulta, m.aceita_convenio
        FROM medicos m
        WHERE m.id = ?
        """,
        (medico_id,),
    )
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")

    # Hospitais — via medico_hospitais quando disponível, fallback hospital_principal
    try:
        hosp_rows = await _fetch_all(
            "SELECT hospital_nome FROM medico_hospitais WHERE medico_id = ? ORDER BY hospital_nome",
            (medico_id,),
        )
        hospitais = [r["hospital_nome"] for r in hosp_rows]
        if not hospitais and medico.get("hospital_principal"):
            hospitais = [medico["hospital_principal"]]
    except Exception:
        hospitais = [medico["hospital_principal"]] if medico.get("hospital_principal") else []

    # Convênios
    conv_rows = await _fetch_all(
        "SELECT nome_convenio FROM convenios WHERE medico_id = ? ORDER BY nome_convenio",
        (medico_id,),
    )
    convenios = [r["nome_convenio"] for r in conv_rows]

    # Procedimentos
    proc_rows = await _fetch_all(
        """
        SELECT nome_procedimento, quantidade, ano
        FROM procedimentos
        WHERE medico_id = ?
        ORDER BY ano DESC, quantidade DESC
        LIMIT 50
        """,
        (medico_id,),
    )
    procedimentos = [
        Procedimento(
            nome=r["nome_procedimento"],
            quantidade=r["quantidade"] or 0,
            ano=r["ano"],
        )
        for r in proc_rows
    ]

    # Avaliações
    aval_rows = await _fetch_all(
        """
        SELECT nota, comentario, aspecto, data_avaliacao, paciente_nome
        FROM avaliacoes
        WHERE medico_id = ?
        ORDER BY data_avaliacao DESC
        LIMIT 20
        """,
        (medico_id,),
    )
    avaliacoes = [
        Avaliacao(
            nota=r["nota"],
            comentario=r.get("comentario"),
            aspecto=r.get("aspecto"),
            data=r["data_avaliacao"],
            paciente=r.get("paciente_nome"),
        )
        for r in aval_rows
    ]

    return MedicoPerfilResponse(
        id=medico["id"],
        nome=medico["nome"],
        crm=medico["crm"],
        especialidade=medico["especialidade"],
        subespecialidade=medico.get("subespecialidade"),
        hospitais=hospitais,
        nota_media=medico.get("nota_media") or 0.0,
        total_avaliacoes=medico.get("total_avaliacoes") or 0,
        anos_experiencia=medico.get("anos_experiencia"),
        valor_consulta=medico.get("valor_consulta"),
        aceita_convenio=bool(medico.get("aceita_convenio", False)),
        convenios=convenios,
        procedimentos=procedimentos,
        avaliacoes=avaliacoes,
    )


# ---------------------------------------------------------------------------
# GET /api/search
# ---------------------------------------------------------------------------

@router.get("/search", response_model=SearchResponse)
async def buscar_medicos(
    q: str = Query(default="", description="Termo de busca livre (nome ou especialidade)"),
    especialidade: str = Query(default=""),
    hospital: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> SearchResponse:
    """Busca médicos em Porto Alegre por nome, especialidade e/ou hospital."""
    conditions = ["m.cidade = 'Porto Alegre'"]
    params: list = []

    if q.strip():
        conditions.append("(m.nome LIKE ? OR m.especialidade LIKE ? OR m.subespecialidade LIKE ?)")
        term = f"%{q.strip()}%"
        params.extend([term, term, term])

    if especialidade.strip():
        conditions.append("m.especialidade LIKE ?")
        params.append(f"%{especialidade.strip()}%")

    where = " AND ".join(conditions)
    offset = (page - 1) * limit

    # Filtro de hospital: pode usar medico_hospitais ou hospital_principal
    join_clause = ""
    if hospital.strip():
        join_clause = "JOIN medico_hospitais mh ON mh.medico_id = m.id"
        conditions.append("mh.hospital_nome LIKE ?")
        params.append(f"%{hospital.strip()}%")
        where = " AND ".join(conditions)

    try:
        count_row = await _fetch_one(
            f"SELECT COUNT(DISTINCT m.id) AS total FROM medicos m {join_clause} WHERE {where}",
            tuple(params),
        )
    except Exception:
        # fallback sem medico_hospitais
        join_clause = ""
        if hospital.strip():
            conditions_fallback = [c for c in conditions if "mh." not in c]
            conditions_fallback.append("m.hospital_principal LIKE ?")
            where = " AND ".join(conditions_fallback)
        count_row = await _fetch_one(
            f"SELECT COUNT(*) AS total FROM medicos m WHERE {where}",
            tuple(params),
        )

    total = count_row["total"] if count_row else 0

    try:
        rows = await _fetch_all(
            f"""
            SELECT DISTINCT m.id, m.nome, m.crm, m.subespecialidade, m.hospital_principal,
                   m.nota_media, m.total_avaliacoes, m.anos_experiencia, m.valor_consulta
            FROM medicos m {join_clause}
            WHERE {where}
            ORDER BY m.nota_media DESC, m.total_avaliacoes DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params) + (limit, offset),
        )
    except Exception:
        rows = await _fetch_all(
            f"""
            SELECT m.id, m.nome, m.crm, m.subespecialidade, m.hospital_principal,
                   m.nota_media, m.total_avaliacoes, m.anos_experiencia, m.valor_consulta
            FROM medicos m
            WHERE {where}
            ORDER BY m.nota_media DESC, m.total_avaliacoes DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params) + (limit, offset),
        )

    return SearchResponse(
        query=q,
        total=total,
        medicos=[_row_to_medico_resumo(r) for r in rows],
    )


# ---------------------------------------------------------------------------
# GET /api/stats
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=StatsResponse)
async def estatisticas() -> StatsResponse:
    """Retorna estatísticas gerais do diretório de Porto Alegre."""
    row = await _fetch_one(
        """
        SELECT
            COUNT(*)                              AS total_medicos,
            SUM(m.total_avaliacoes)               AS total_avaliacoes,
            COUNT(DISTINCT m.especialidade)       AS total_especialidades,
            COUNT(DISTINCT m.hospital_principal)  AS total_hospitais,
            ROUND(AVG(m.nota_media), 2)           AS nota_media_geral
        FROM medicos m
        WHERE m.cidade = 'Porto Alegre'
        """
    )

    return StatsResponse(
        total_medicos=row["total_medicos"] or 0,
        total_avaliacoes=row["total_avaliacoes"] or 0,
        total_especialidades=row["total_especialidades"] or 0,
        total_hospitais=row["total_hospitais"] or 0,
        nota_media_geral=row["nota_media_geral"] or 0.0,
    )
