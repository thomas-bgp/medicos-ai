"""
seed.py — Popula o banco SQLite com dados MASSIVOS e realistas de médicos brasileiros.
Execute a partir de C:/Projects/medicos-ai/ com: python backend/seed.py

Gera: ~2000 médicos, ~25000 avaliações, ~12000 procedimentos, ~10000 convênios
"""

import sqlite3
import random
import datetime
import os
import sys

# Ensure backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seed_data import (
    ESPECIALIDADES_COMPLETAS,
    PROCEDIMENTOS_POR_ESPECIALIDADE,
    HOSPITAIS_POR_CIDADE,
    NOMES_MASCULINOS,
    NOMES_FEMININOS,
    SOBRENOMES,
    CONVENIOS_LISTA,
    COMENTARIOS,
    VALOR_CONSULTA,
    ASPECTOS_AVALIACAO,
    NOMES_PACIENTES,
)

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "medicos.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
NUM_MEDICOS = 2000
AVALIACOES_POR_MEDICO = (5, 30)  # min, max
PROCS_POR_MEDICO = (3, 12)      # min, max procedimentos por médico
CONVENIOS_POR_MEDICO = (2, 8)   # min, max

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------
DDL = """
CREATE TABLE IF NOT EXISTS medicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    crm TEXT NOT NULL UNIQUE,
    especialidade TEXT NOT NULL,
    subespecialidade TEXT,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL,
    hospital_principal TEXT,
    aceita_convenio BOOLEAN DEFAULT 1,
    valor_consulta REAL,
    nota_media REAL DEFAULT 0.0,
    total_avaliacoes INTEGER DEFAULT 0,
    anos_experiencia INTEGER
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    nota REAL NOT NULL CHECK (nota >= 1.0 AND nota <= 5.0),
    comentario TEXT,
    aspecto TEXT,
    data_avaliacao DATE NOT NULL,
    paciente_nome TEXT
);

CREATE TABLE IF NOT EXISTS procedimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    nome_procedimento TEXT NOT NULL,
    codigo_tuss TEXT,
    quantidade INTEGER DEFAULT 0,
    ano INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS convenios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    nome_convenio TEXT NOT NULL
);
"""

INDICES = [
    "CREATE INDEX IF NOT EXISTS idx_medicos_especialidade ON medicos(especialidade);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_subespecialidade ON medicos(subespecialidade);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_cidade_estado ON medicos(cidade, estado);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_nota ON medicos(nota_media DESC);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_nome ON medicos(nome);",
    "CREATE INDEX IF NOT EXISTS idx_avaliacoes_medico ON avaliacoes(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_procedimentos_medico ON procedimentos(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_procedimentos_nome ON procedimentos(nome_procedimento);",
    "CREATE INDEX IF NOT EXISTS idx_convenios_medico ON convenios(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_convenios_nome ON convenios(nome_convenio);",
]

# ---------------------------------------------------------------------------
# Distribuição de peso por cidade (capitais maiores = mais médicos)
# ---------------------------------------------------------------------------
PESO_CIDADES = {
    "São Paulo": 20,
    "Rio de Janeiro": 14,
    "Belo Horizonte": 8,
    "Curitiba": 7,
    "Porto Alegre": 7,
    "Brasília": 7,
    "Salvador": 6,
    "Recife": 5,
    "Fortaleza": 5,
    "Goiânia": 4,
    "Campinas": 4,
    "Florianópolis": 3,
    "Ribeirão Preto": 3,
    "Vitória": 2,
    "Natal": 2,
    "Manaus": 2,
    "Belém": 2,
    "São José dos Campos": 2,
    "Campo Grande": 2,
    "São Luís": 2,
}

# Especialidades com mais peso (mais comuns)
PESO_ESPECIALIDADES = {
    "Cardiologia": 8,
    "Ortopedia e Traumatologia": 8,
    "Dermatologia": 6,
    "Ginecologia e Obstetrícia": 7,
    "Pediatria": 7,
    "Neurologia": 5,
    "Oftalmologia": 5,
    "Urologia": 4,
    "Psiquiatria": 5,
    "Oncologia Clínica": 3,
    "Endocrinologia": 4,
    "Gastroenterologia": 4,
    "Otorrinolaringologia": 4,
    "Cirurgia Geral": 6,
    "Cirurgia Plástica": 4,
    "Neurocirurgia": 3,
    "Cirurgia Cardiovascular": 2,
    "Cirurgia Vascular": 3,
    "Pneumologia": 3,
    "Nefrologia": 2,
    "Reumatologia": 3,
    "Hematologia": 2,
    "Infectologia": 2,
    "Geriatria": 3,
    "Medicina do Esporte": 2,
    "Anestesiologia": 4,
    "Medicina Intensiva": 3,
    "Medicina da Família e Comunidade": 4,
    "Mastologia": 2,
    "Cirurgia Torácica": 1,
    "Cirurgia de Cabeça e Pescoço": 1,
    "Cirurgia Pediátrica": 1,
    "Coloproctologia": 2,
    "Angiologia": 2,
    "Nutrologia": 2,
    "Medicina Física e Reabilitação": 2,
    "Radiologia e Diagnóstico por Imagem": 2,
    "Patologia": 1,
    "Genética Médica": 1,
    "Medicina Nuclear": 1,
    "Acupuntura": 1,
    "Medicina do Trabalho": 1,
    "Medicina Legal e Perícia Médica": 1,
    "Homeopatia": 1,
    "Cirurgia do Aparelho Digestivo": 2,
    "Cirurgia da Mão": 1,
    "Alergia e Imunologia": 2,
    "Radioterapia": 1,
    "Medicina de Emergência": 2,
    "Medicina Preventiva e Social": 1,
}


# ---------------------------------------------------------------------------
# Geração de dados
# ---------------------------------------------------------------------------

def weighted_choice(weight_dict: dict) -> str:
    """Escolhe uma chave proporcionalmente ao peso."""
    keys = list(weight_dict.keys())
    weights = [weight_dict[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]


def gerar_crm(estado: str, usado: set) -> str:
    while True:
        numero = random.randint(10000, 999999)
        crm = f"CRM/{estado} {numero}"
        if crm not in usado:
            usado.add(crm)
            return crm


def gerar_nome() -> str:
    """Gera nome com prefixo Dr./Dra. baseado no gênero."""
    if random.random() < 0.45:
        primeiro = random.choice(NOMES_FEMININOS)
        prefixo = "Dra."
    else:
        primeiro = random.choice(NOMES_MASCULINOS)
        prefixo = "Dr."
    meio = random.choice(SOBRENOMES)
    ultimo = random.choice(SOBRENOMES)
    while ultimo == meio:
        ultimo = random.choice(SOBRENOMES)
    return f"{prefixo} {primeiro} {meio} {ultimo}"


def gerar_data_avaliacao() -> str:
    inicio = datetime.date(2022, 1, 1)
    fim = datetime.date(2026, 3, 19)
    delta = (fim - inicio).days
    return (inicio + datetime.timedelta(days=random.randint(0, delta))).isoformat()


def escolher_nota() -> float:
    """Curva realista: média ~4.1, poucos abaixo de 3."""
    r = random.random()
    if r < 0.02:
        return round(random.uniform(1.0, 2.0), 1)
    elif r < 0.06:
        return round(random.uniform(2.0, 3.0), 1)
    elif r < 0.18:
        return round(random.uniform(3.0, 3.9), 1)
    elif r < 0.48:
        return round(random.uniform(3.9, 4.5), 1)
    else:
        return round(random.uniform(4.5, 5.0), 1)


def escolher_comentario(nota: float) -> str:
    if nota >= 4.0:
        return random.choice(COMENTARIOS["alto"])
    elif nota >= 3.0:
        return random.choice(COMENTARIOS["medio"])
    else:
        return random.choice(COMENTARIOS["baixo"])


def get_estado_for_cidade(cidade: str) -> str:
    """Extrai UF do dict HOSPITAIS_POR_CIDADE."""
    info = HOSPITAIS_POR_CIDADE[cidade]
    # info é (estado, [hospitais])
    return info[0]


def get_hospitais_for_cidade(cidade: str) -> list:
    return HOSPITAIS_POR_CIDADE[cidade][1]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    random.seed(42)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Banco anterior removido: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    cur = conn.cursor()

    # Criar tabelas
    for stmt in DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    print("Tabelas criadas.")

    # Filtrar apenas especialidades que existem no seed_data
    available_specs = set(ESPECIALIDADES_COMPLETAS.keys())
    peso_filtrado = {k: v for k, v in PESO_ESPECIALIDADES.items() if k in available_specs}

    # Se alguma especialidade do seed_data não tem peso, dar peso 1
    for spec in available_specs:
        if spec not in peso_filtrado:
            peso_filtrado[spec] = 1

    # Filtrar cidades disponíveis
    available_cities = set(HOSPITAIS_POR_CIDADE.keys())
    peso_cidades_filtrado = {k: v for k, v in PESO_CIDADES.items() if k in available_cities}
    for city in available_cities:
        if city not in peso_cidades_filtrado:
            peso_cidades_filtrado[city] = 1

    # ------------------------------------------------------------------
    # Inserir médicos
    # ------------------------------------------------------------------
    crms_usados: set = set()
    medicos_info = []  # (id, especialidade)

    for i in range(NUM_MEDICOS):
        nome = gerar_nome()
        especialidade = weighted_choice(peso_filtrado)
        subesp_list = ESPECIALIDADES_COMPLETAS.get(especialidade, [])
        subespecialidade = random.choice(subesp_list) if subesp_list else None
        cidade = weighted_choice(peso_cidades_filtrado)
        estado = get_estado_for_cidade(cidade)
        hospitais = get_hospitais_for_cidade(cidade)
        crm = gerar_crm(estado, crms_usados)
        hospital = random.choice(hospitais)
        aceita_convenio = 1 if random.random() > 0.12 else 0

        # Valor da consulta
        val_range = VALOR_CONSULTA.get(especialidade, (300, 700))
        valor = round(random.uniform(val_range[0], val_range[1]) / 10) * 10

        anos_exp = random.randint(2, 40)

        cur.execute(
            """INSERT INTO medicos
               (nome, crm, especialidade, subespecialidade, cidade, estado,
                hospital_principal, aceita_convenio, valor_consulta, anos_experiencia)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nome, crm, especialidade, subespecialidade, cidade, estado,
             hospital, aceita_convenio, valor, anos_exp),
        )
        medicos_info.append((cur.lastrowid, especialidade))

        if (i + 1) % 500 == 0:
            conn.commit()
            print(f"  {i + 1} médicos inseridos...")

    conn.commit()
    print(f"{len(medicos_info)} médicos inseridos no total.")

    # ------------------------------------------------------------------
    # Inserir avaliações
    # ------------------------------------------------------------------
    total_avaliacoes = 0
    notas_por_medico: dict = {}
    batch = []

    for medico_id, _ in medicos_info:
        qtd = random.randint(*AVALIACOES_POR_MEDICO)
        notas: list = []
        for _ in range(qtd):
            nota = escolher_nota()
            notas.append(nota)
            comentario = escolher_comentario(nota)
            aspecto = random.choice(ASPECTOS_AVALIACAO)
            data_av = gerar_data_avaliacao()
            paciente = random.choice(NOMES_PACIENTES)
            batch.append((medico_id, nota, comentario, aspecto, data_av, paciente))
        notas_por_medico[medico_id] = notas
        total_avaliacoes += qtd

        if len(batch) >= 5000:
            cur.executemany(
                """INSERT INTO avaliacoes
                   (medico_id, nota, comentario, aspecto, data_avaliacao, paciente_nome)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                batch,
            )
            conn.commit()
            batch = []

    if batch:
        cur.executemany(
            """INSERT INTO avaliacoes
               (medico_id, nota, comentario, aspecto, data_avaliacao, paciente_nome)
               VALUES (?, ?, ?, ?, ?, ?)""",
            batch,
        )
        conn.commit()

    print(f"{total_avaliacoes} avaliações inseridas.")

    # UPDATE nota_media e total_avaliacoes
    update_batch = []
    for medico_id, notas in notas_por_medico.items():
        media = round(sum(notas) / len(notas), 2)
        update_batch.append((media, len(notas), medico_id))

    cur.executemany(
        "UPDATE medicos SET nota_media = ?, total_avaliacoes = ? WHERE id = ?",
        update_batch,
    )
    conn.commit()
    print("nota_media e total_avaliacoes atualizados.")

    # ------------------------------------------------------------------
    # Inserir procedimentos
    # ------------------------------------------------------------------
    total_procedimentos = 0
    proc_batch = []

    for medico_id, especialidade in medicos_info:
        procs = PROCEDIMENTOS_POR_ESPECIALIDADE.get(especialidade, [])
        if not procs:
            continue

        # Cada médico tem entre 3-12 procedimentos
        n_procs = min(random.randint(*PROCS_POR_MEDICO), len(procs))
        selected_procs = random.sample(procs, n_procs)

        for nome_proc, codigo_tuss in selected_procs:
            quantidade = random.randint(5, 600)
            ano = random.randint(2019, 2025)
            proc_batch.append((medico_id, nome_proc, codigo_tuss, quantidade, ano))
            total_procedimentos += 1

        if len(proc_batch) >= 5000:
            cur.executemany(
                """INSERT INTO procedimentos
                   (medico_id, nome_procedimento, codigo_tuss, quantidade, ano)
                   VALUES (?, ?, ?, ?, ?)""",
                proc_batch,
            )
            conn.commit()
            proc_batch = []

    if proc_batch:
        cur.executemany(
            """INSERT INTO procedimentos
               (medico_id, nome_procedimento, codigo_tuss, quantidade, ano)
               VALUES (?, ?, ?, ?, ?)""",
            proc_batch,
        )
        conn.commit()

    print(f"{total_procedimentos} procedimentos inseridos.")

    # ------------------------------------------------------------------
    # Inserir convênios
    # ------------------------------------------------------------------
    total_convenios = 0
    conv_batch = []

    for medico_id, _ in medicos_info:
        qtd_conv = random.randint(*CONVENIOS_POR_MEDICO)
        convenios_medico = random.sample(CONVENIOS_LISTA, min(qtd_conv, len(CONVENIOS_LISTA)))
        for conv in convenios_medico:
            conv_batch.append((medico_id, conv))
            total_convenios += 1

    cur.executemany(
        "INSERT INTO convenios (medico_id, nome_convenio) VALUES (?, ?)",
        conv_batch,
    )
    conn.commit()
    print(f"{total_convenios} convênios inseridos.")

    # ------------------------------------------------------------------
    # Criar índices (após inserção = mais rápido)
    # ------------------------------------------------------------------
    for idx in INDICES:
        cur.execute(idx)
    conn.commit()
    print("Índices criados.")

    # ------------------------------------------------------------------
    # Resumo final
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)

    cur.execute("SELECT COUNT(*) FROM medicos")
    print(f"  Médicos:        {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM avaliacoes")
    print(f"  Avaliações:     {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM procedimentos")
    print(f"  Procedimentos:  {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM convenios")
    print(f"  Convênios:      {cur.fetchone()[0]:,}")
    cur.execute("SELECT AVG(nota_media) FROM medicos")
    print(f"  Nota média:     {cur.fetchone()[0]:.2f}")
    cur.execute("SELECT COUNT(DISTINCT especialidade) FROM medicos")
    print(f"  Especialidades: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(DISTINCT cidade) FROM medicos")
    print(f"  Cidades:        {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(DISTINCT subespecialidade) FROM medicos WHERE subespecialidade IS NOT NULL")
    print(f"  Subespecialid.: {cur.fetchone()[0]}")

    # Top 5 especialidades
    print("\nTop 10 especialidades:")
    cur.execute("SELECT especialidade, COUNT(*) as c FROM medicos GROUP BY especialidade ORDER BY c DESC LIMIT 10")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Médicos por cidade
    print("\nMédicos por cidade:")
    cur.execute("SELECT cidade, COUNT(*) as c FROM medicos GROUP BY cidade ORDER BY c DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print(f"\nBanco criado em: {DB_PATH}")


if __name__ == "__main__":
    main()
