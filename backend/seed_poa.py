"""
seed_poa.py — Popula o banco SQLite com 5000 médicos EXCLUSIVAMENTE de Porto Alegre / RS.

Execute a partir de C:/Projects/medicos-ai/ com:
    python backend/seed_poa.py

Gera:  ~5000 médicos, ~100.000 avaliações, ~50.000 procedimentos, ~30.000 convênios.
Banco: data/medicos.db
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
CIDADE = "Porto Alegre"
ESTADO = "RS"
NUM_MEDICOS = 5000
AVALIACOES_POR_MEDICO = (8, 40)   # min, max  — média ~20  → ~100.000 total
PROCS_POR_MEDICO     = (5, 15)    # min, max procedimentos por médico
CONVENIOS_POR_MEDICO = (3, 8)     # min, max convênios por médico
HOSPITAIS_POR_MEDICO = (1, 3)     # min, max hospitais vinculados

# ---------------------------------------------------------------------------
# Hospitais REAIS de Porto Alegre
# ---------------------------------------------------------------------------
HOSPITAIS_POA = [
    "Hospital Moinhos de Vento",
    "Hospital São Lucas da PUCRS",
    "Hospital de Clínicas de Porto Alegre (HCPA)",
    "Hospital Nossa Senhora da Conceição",
    "Hospital Ernesto Dornelles",
    "Hospital Divina Providência",
    "Hospital Mãe de Deus",
    "Hospital Cristo Redentor",
    "Santa Casa de Misericórdia de Porto Alegre",
    "Hospital Presidente Vargas",
    "Hospital Fêmina",
    "Hospital da Criança Santo Antônio",
    "Hospital Porto Alegre",
    "Hospital Parque Belém",
    "Hospital Dom Vicente Scherer",
    "Hospital São José (Complexo Hospitalar Santa Casa)",
    "Hospital Vila Nova Star (POA)",
    "Hospital Restinga e Extremo Sul",
    "Hospital da ULBRA",
    "Clínica Viva - Centro Clínico Moinhos",
    "Instituto de Cardiologia do RS",
    "Hospital Banco de Olhos",
    "Centro de Oncologia Hospital Moinhos de Vento",
]

# ---------------------------------------------------------------------------
# Pesos de especialidades (favorece as mais prevalentes em POA)
# ---------------------------------------------------------------------------
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
    "Endocrinologia e Metabologia": 4,
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
    "Hematologia e Hemoterapia": 2,
    "Infectologia": 2,
    "Geriatria e Gerontologia": 3,
    "Medicina do Esporte": 2,
    "Anestesiologia": 4,
    "Medicina Intensiva": 3,
    "Medicina de Família e Comunidade": 4,
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
# DDL — mesmo schema do seed.py original + tabela medico_hospitais
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

CREATE TABLE IF NOT EXISTS medico_hospitais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    hospital TEXT NOT NULL
);
"""

INDICES = [
    "CREATE INDEX IF NOT EXISTS idx_medicos_especialidade ON medicos(especialidade);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_subespecialidade ON medicos(subespecialidade);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_cidade_estado ON medicos(cidade, estado);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_nota ON medicos(nota_media DESC);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_nome ON medicos(nome);",
    "CREATE INDEX IF NOT EXISTS idx_medicos_hospital ON medicos(hospital_principal);",
    "CREATE INDEX IF NOT EXISTS idx_avaliacoes_medico ON avaliacoes(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_procedimentos_medico ON procedimentos(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_procedimentos_nome ON procedimentos(nome_procedimento);",
    "CREATE INDEX IF NOT EXISTS idx_convenios_medico ON convenios(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_convenios_nome ON convenios(nome_convenio);",
    "CREATE INDEX IF NOT EXISTS idx_medico_hospitais_medico ON medico_hospitais(medico_id);",
    "CREATE INDEX IF NOT EXISTS idx_medico_hospitais_hospital ON medico_hospitais(hospital);",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def weighted_choice(weight_dict: dict) -> str:
    keys    = list(weight_dict.keys())
    weights = [weight_dict[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]


def gerar_crm(usado: set) -> str:
    while True:
        numero = random.randint(10000, 999999)
        crm    = f"CRM/RS {numero}"
        if crm not in usado:
            usado.add(crm)
            return crm


def gerar_nome() -> str:
    if random.random() < 0.45:
        primeiro = random.choice(NOMES_FEMININOS)
        prefixo  = "Dra."
    else:
        primeiro = random.choice(NOMES_MASCULINOS)
        prefixo  = "Dr."
    meio   = random.choice(SOBRENOMES)
    ultimo = random.choice(SOBRENOMES)
    while ultimo == meio:
        ultimo = random.choice(SOBRENOMES)
    return f"{prefixo} {primeiro} {meio} {ultimo}"


def gerar_data_avaliacao() -> str:
    inicio = datetime.date(2022, 1, 1)
    fim    = datetime.date(2026, 3, 19)
    delta  = (fim - inicio).days
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

    # Filtrar apenas especialidades que existem em seed_data
    available_specs   = set(ESPECIALIDADES_COMPLETAS.keys())
    peso_filtrado     = {k: v for k, v in PESO_ESPECIALIDADES.items() if k in available_specs}
    # Especialidades sem peso explícito recebem peso 1
    for spec in available_specs:
        if spec not in peso_filtrado:
            peso_filtrado[spec] = 1

    # ------------------------------------------------------------------
    # 1. Inserir médicos
    # ------------------------------------------------------------------
    crms_usados: set = set()
    medicos_info     = []   # lista de (medico_id, especialidade, hospitais_vinculados)

    print(f"Gerando {NUM_MEDICOS} médicos em Porto Alegre / RS...")
    medicos_rows = []

    for i in range(NUM_MEDICOS):
        nome          = gerar_nome()
        especialidade = weighted_choice(peso_filtrado)
        subesp_list   = ESPECIALIDADES_COMPLETAS.get(especialidade, [])
        subesp        = random.choice(subesp_list) if subesp_list else None
        crm           = gerar_crm(crms_usados)
        aceita_conv   = 1 if random.random() > 0.12 else 0

        # Hospital principal (1 dos 23 reais de POA)
        hospital_principal = random.choice(HOSPITAIS_POA)

        # Valor da consulta
        val_range = VALOR_CONSULTA.get(especialidade, (300, 700))
        valor     = round(random.uniform(val_range[0], val_range[1]) / 10) * 10

        anos_exp = random.randint(2, 40)

        medicos_rows.append((
            nome, crm, especialidade, subesp,
            CIDADE, ESTADO, hospital_principal,
            aceita_conv, valor, anos_exp,
        ))

    cur.executemany(
        """INSERT INTO medicos
           (nome, crm, especialidade, subespecialidade, cidade, estado,
            hospital_principal, aceita_convenio, valor_consulta, anos_experiencia)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        medicos_rows,
    )
    conn.commit()

    # Recuperar IDs na ordem de inserção
    cur.execute("SELECT id, especialidade FROM medicos ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        medicos_info.append((row[0], row[1]))

    print(f"{len(medicos_info)} médicos inseridos.")

    # ------------------------------------------------------------------
    # 2. Inserir medico_hospitais (1-3 por médico, inclui o principal)
    # ------------------------------------------------------------------
    print("Gerando vínculos de hospitais por médico...")
    mh_batch = []

    for medico_id, _ in medicos_info:
        # principal já conhecido pelo INSERT order — mas buscamos por id
        cur.execute("SELECT hospital_principal FROM medicos WHERE id = ?", (medico_id,))
        principal = cur.fetchone()[0]

        n_extras = random.randint(0, 2)   # 0-2 hospitais adicionais além do principal
        pool      = [h for h in HOSPITAIS_POA if h != principal]
        extras    = random.sample(pool, min(n_extras, len(pool)))

        hospitais_vinculados = [principal] + extras
        for h in hospitais_vinculados:
            mh_batch.append((medico_id, h))

        if len(mh_batch) >= 10_000:
            cur.executemany(
                "INSERT INTO medico_hospitais (medico_id, hospital) VALUES (?, ?)",
                mh_batch,
            )
            conn.commit()
            mh_batch = []

    if mh_batch:
        cur.executemany(
            "INSERT INTO medico_hospitais (medico_id, hospital) VALUES (?, ?)",
            mh_batch,
        )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM medico_hospitais")
    print(f"{cur.fetchone()[0]} vínculos medico_hospitais inseridos.")

    # ------------------------------------------------------------------
    # 3. Inserir avaliações  (~100.000 total)
    # ------------------------------------------------------------------
    print("Gerando avaliações...")
    total_avaliacoes = 0
    notas_por_medico: dict = {}
    batch = []

    for medico_id, _ in medicos_info:
        qtd   = random.randint(*AVALIACOES_POR_MEDICO)
        notas: list = []
        for _ in range(qtd):
            nota      = escolher_nota()
            notas.append(nota)
            comentario = escolher_comentario(nota)
            aspecto    = random.choice(ASPECTOS_AVALIACAO)
            data_av    = gerar_data_avaliacao()
            paciente   = random.choice(NOMES_PACIENTES)
            batch.append((medico_id, nota, comentario, aspecto, data_av, paciente))
        notas_por_medico[medico_id] = notas
        total_avaliacoes += qtd

        if len(batch) >= 10_000:
            cur.executemany(
                """INSERT INTO avaliacoes
                   (medico_id, nota, comentario, aspecto, data_avaliacao, paciente_nome)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                batch,
            )
            conn.commit()
            batch = []
            print(f"  {total_avaliacoes:,} avaliações inseridas até agora...")

    if batch:
        cur.executemany(
            """INSERT INTO avaliacoes
               (medico_id, nota, comentario, aspecto, data_avaliacao, paciente_nome)
               VALUES (?, ?, ?, ?, ?, ?)""",
            batch,
        )
        conn.commit()

    print(f"{total_avaliacoes:,} avaliações inseridas.")

    # UPDATE nota_media e total_avaliacoes
    update_batch = [
        (round(sum(notas) / len(notas), 2), len(notas), mid)
        for mid, notas in notas_por_medico.items()
    ]
    cur.executemany(
        "UPDATE medicos SET nota_media = ?, total_avaliacoes = ? WHERE id = ?",
        update_batch,
    )
    conn.commit()
    print("nota_media e total_avaliacoes atualizados.")

    # ------------------------------------------------------------------
    # 4. Inserir procedimentos (5-15 por médico)
    # ------------------------------------------------------------------
    print("Gerando procedimentos...")
    total_procs = 0
    proc_batch  = []

    for medico_id, especialidade in medicos_info:
        procs = PROCEDIMENTOS_POR_ESPECIALIDADE.get(especialidade, [])
        if not procs:
            continue

        n_procs        = min(random.randint(*PROCS_POR_MEDICO), len(procs))
        selected_procs = random.sample(procs, n_procs)

        for nome_proc, codigo_tuss in selected_procs:
            quantidade = random.randint(5, 800)
            ano        = random.randint(2019, 2025)
            proc_batch.append((medico_id, nome_proc, codigo_tuss, quantidade, ano))
            total_procs += 1

        if len(proc_batch) >= 10_000:
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

    print(f"{total_procs:,} procedimentos inseridos.")

    # ------------------------------------------------------------------
    # 5. Inserir convênios (3-8 por médico)
    # ------------------------------------------------------------------
    print("Gerando convênios...")
    total_convenios = 0
    conv_batch      = []

    for medico_id, _ in medicos_info:
        qtd_conv        = random.randint(*CONVENIOS_POR_MEDICO)
        convenios_medico = random.sample(CONVENIOS_LISTA, min(qtd_conv, len(CONVENIOS_LISTA)))
        for conv in convenios_medico:
            conv_batch.append((medico_id, conv))
            total_convenios += 1

    cur.executemany(
        "INSERT INTO convenios (medico_id, nome_convenio) VALUES (?, ?)",
        conv_batch,
    )
    conn.commit()
    print(f"{total_convenios:,} convênios inseridos.")

    # ------------------------------------------------------------------
    # 6. Criar índices APÓS todos os inserts (muito mais rápido)
    # ------------------------------------------------------------------
    print("Criando índices...")
    for idx in INDICES:
        cur.execute(idx)
    conn.commit()
    print("Índices criados.")

    # ------------------------------------------------------------------
    # Resumo final
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("RESUMO FINAL — Porto Alegre / RS")
    print("=" * 65)

    cur.execute("SELECT COUNT(*) FROM medicos")
    print(f"  Médicos:              {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM avaliacoes")
    print(f"  Avaliações:           {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM procedimentos")
    print(f"  Procedimentos:        {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM convenios")
    print(f"  Convênios:            {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM medico_hospitais")
    print(f"  Vínculos hospitais:   {cur.fetchone()[0]:,}")
    cur.execute("SELECT AVG(nota_media) FROM medicos")
    print(f"  Nota média geral:     {cur.fetchone()[0]:.2f}")
    cur.execute("SELECT COUNT(DISTINCT especialidade) FROM medicos")
    print(f"  Especialidades:       {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(DISTINCT subespecialidade) FROM medicos WHERE subespecialidade IS NOT NULL")
    print(f"  Subespecialidades:    {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(DISTINCT cidade) FROM medicos")
    print(f"  Cidades:              {cur.fetchone()[0]}")

    print("\nTop 15 especialidades:")
    cur.execute(
        "SELECT especialidade, COUNT(*) as c FROM medicos GROUP BY especialidade ORDER BY c DESC LIMIT 15"
    )
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\nMédicos por hospital principal (Top 15):")
    cur.execute(
        "SELECT hospital_principal, COUNT(*) as c FROM medicos GROUP BY hospital_principal ORDER BY c DESC LIMIT 15"
    )
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\nVínculos por hospital (medico_hospitais, Top 15):")
    cur.execute(
        "SELECT hospital, COUNT(*) as c FROM medico_hospitais GROUP BY hospital ORDER BY c DESC LIMIT 15"
    )
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print(f"\nBanco criado em: {DB_PATH}")


if __name__ == "__main__":
    main()
