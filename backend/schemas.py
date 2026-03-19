from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []


class ChatResponse(BaseModel):
    response: str
    sql_query: str | None = None
    results_count: int | None = None


# ---------------------------------------------------------------------------
# Browse — especialidades
# ---------------------------------------------------------------------------

class EspecialidadeItem(BaseModel):
    especialidade: str
    count: int
    slug: str


class EspecialidadesResponse(BaseModel):
    especialidades: list[EspecialidadeItem]


class MedicoResumo(BaseModel):
    id: int
    nome: str
    crm: str
    subespecialidade: str | None = None
    hospital_principal: str | None = None
    nota_media: float
    total_avaliacoes: int
    anos_experiencia: int | None = None
    valor_consulta: float | None = None


class EspecialidadeDetalheResponse(BaseModel):
    especialidade: str
    total: int
    medicos: list[MedicoResumo]


# ---------------------------------------------------------------------------
# Browse — hospitais
# ---------------------------------------------------------------------------

class HospitalItem(BaseModel):
    hospital: str
    count: int
    slug: str


class HospitaisResponse(BaseModel):
    hospitais: list[HospitalItem]


class HospitalDetalheResponse(BaseModel):
    hospital: str
    total: int
    medicos: list[MedicoResumo]


# ---------------------------------------------------------------------------
# Perfil completo do médico
# ---------------------------------------------------------------------------

class Procedimento(BaseModel):
    nome: str
    quantidade: int
    ano: int


class Avaliacao(BaseModel):
    nota: float
    comentario: str | None = None
    aspecto: str | None = None
    data: str
    paciente: str | None = None


class MedicoPerfilResponse(BaseModel):
    id: int
    nome: str
    crm: str
    especialidade: str
    subespecialidade: str | None = None
    hospitais: list[str]
    nota_media: float
    total_avaliacoes: int
    anos_experiencia: int | None = None
    valor_consulta: float | None = None
    aceita_convenio: bool
    convenios: list[str]
    procedimentos: list[Procedimento]
    avaliacoes: list[Avaliacao]


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class SearchResponse(BaseModel):
    query: str
    total: int
    medicos: list[MedicoResumo]


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    total_medicos: int
    total_avaliacoes: int
    total_especialidades: int
    total_hospitais: int
    nota_media_geral: float
