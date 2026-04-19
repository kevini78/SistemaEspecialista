"""
Base de Conhecimento do Sistema Especialista.

Representação do conhecimento: regras de produção ponderadas por
Fatores de Certeza (CF) no estilo MYCIN, combinadas com lógica fuzzy
para os graus de intensidade dos sintomas.

Cada linha da tabela clínica foi convertida em um nível esperado de
intensidade (0.0 a 1.0) e um peso de evidência (quão discriminativo
aquele sintoma é para aquela doença).
"""

from dataclasses import dataclass
from typing import Dict, List


# --------------------------------------------------------------------
# 1) Termos fuzzy de intensidade dos sintomas
# --------------------------------------------------------------------

INTENSITY_LEVELS: Dict[str, float] = {
    "ausente":       0.00,
    "muito_leve":    0.15,
    "leve":          0.33,
    "moderado":      0.55,
    "intenso":       0.80,
    "muito_intenso": 1.00,
}

INTENSITY_LABELS = {
    "ausente":       "Ausente",
    "muito_leve":    "Muito leve",
    "leve":          "Leve",
    "moderado":      "Moderado",
    "intenso":       "Intenso",
    "muito_intenso": "Muito intenso",
}


# --------------------------------------------------------------------
# 2) Catálogo de sintomas (as "variáveis linguísticas" do sistema)
# --------------------------------------------------------------------
SYMPTOMS: Dict[str, str] = {
    "inicio_subito":        "Início súbito dos sintomas",
    "febre":                "Febre",
    "dor_cabeca":           "Dor de cabeça",
    "dor_atras_olhos":      "Dor atrás dos olhos",
    "dor_muscular":         "Dor muscular",
    "cansaco":              "Cansaço / fadiga",
    "tosse_seca":           "Tosse seca",
    "tosse_catarro":        "Tosse com catarro",
    "coriza":               "Coriza (nariz escorrendo)",
    "congestao_nasal":      "Congestão nasal",
    "dor_garganta":         "Dor de garganta",
    "falta_ar":             "Falta de ar",
    "perda_olfato_paladar": "Perda de olfato/paladar",
    "manchas_pele":         "Manchas na pele",
    "nausea_vomito":        "Náusea / vômito",
    "dor_facial":           "Dor/pressão facial (sinusal)",
}


# --------------------------------------------------------------------
# 3) Regras de produção com Fatores de Certeza
# --------------------------------------------------------------------
# Para cada doença listamos evidências no formato:
#   (sintoma, intensidade_esperada [0..1], peso_cf [-1..1])
#
# - peso_cf > 0  -> sintoma favorece a hipótese
# - peso_cf < 0  -> sintoma enfraquece a hipótese (contra-evidência)
#
# O CF da regra no momento da execução é:
#   cf_regra = peso_cf * similaridade_fuzzy(esperado, observado)
#
# onde similaridade = 1 - |esperado - observado|, saturada em 0.
# CFs positivos e negativos são combinados pelas fórmulas de MYCIN.
# --------------------------------------------------------------------

@dataclass
class Evidence:
    symptom: str
    expected: float   # intensidade esperada (fuzzy)
    weight: float     # peso/CF máximo dessa evidência

    def similarity(self, observed: float) -> float:
        # Similaridade fuzzy quadratica: perfeita em exp==obs, cai
        # rapidamente a medida que se afasta. Essa forma mais "picuda"
        # evita que um sintoma esperado com intensidade intermediaria
        # (ex.: "leve") dispare fortemente quando o observado e "ausente".
        diff = abs(self.expected - observed)
        return max(0.0, 1.0 - diff) ** 2


DISEASES: Dict[str, str] = {
    "resfriado": "Resfriado comum",
    "gripe":     "Gripe (Influenza)",
    "h1n1":      "Gripe H1N1",
    "covid":     "COVID-19",
    "dengue":    "Dengue",
    "sinusite":  "Sinusite",
}


# Convenção semântica:
#
# POSITIVA:            Evidence(sintoma, esperado, +peso)
#   - Favorece a hipótese quando o observado está próximo do esperado.
#
# CONTRA-EVIDÊNCIA:    Evidence(sintoma, 1.00, -peso)
#   - Só penaliza quando o sintoma aparece com intensidade alta.
#     Se ausente, similaridade = 0 e não há penalidade indevida.
#
# AUSÊNCIA DE MARCADOR: Evidence(sintoma, 0.00, -peso)
#   - Penaliza quando um sintoma-chave está AUSENTE em uma doença que
#     normalmente o apresenta (ex.: dengue sem dor atrás dos olhos,
#     COVID sem perda de olfato). Garante separação entre hipóteses
#     com sintomas gerais parecidos mas marcadores distintos.

RULES: Dict[str, List[Evidence]] = {
    # ----------------------------- RESFRIADO -----------------------------
    # Perfil: início gradual, sem febre, sintomas leves com predomínio de
    # coriza / congestão / dor de garganta.
    "resfriado": [
        # Positivas (precisam de sintomas respiratorios para disparar)
        Evidence("coriza",               0.80,  0.60),
        Evidence("congestao_nasal",      0.80,  0.55),
        Evidence("dor_garganta",         0.70,  0.45),
        Evidence("tosse_seca",           0.33,  0.15),
        Evidence("dor_muscular",         0.33,  0.10),
        Evidence("cansaco",              0.33,  0.08),
        # Contra-evidências (só penalizam se sintoma intenso)
        Evidence("inicio_subito",        1.00, -0.55),
        Evidence("febre",                1.00, -0.75),
        Evidence("dor_cabeca",           1.00, -0.45),
        Evidence("dor_muscular",         1.00, -0.55),
        Evidence("cansaco",              1.00, -0.40),
        Evidence("dor_atras_olhos",      1.00, -0.60),
        Evidence("falta_ar",             1.00, -0.75),
        Evidence("perda_olfato_paladar", 1.00, -0.70),
        Evidence("manchas_pele",         1.00, -0.80),
        Evidence("dor_facial",           1.00, -0.45),
        Evidence("tosse_catarro",        1.00, -0.45),
    ],

    # ------------------------------- GRIPE -------------------------------
    # Perfil: início súbito, febre alta (38-39), dor muscular intensa,
    # cansaço intenso, tosse seca.
    "gripe": [
        # Positivas
        Evidence("inicio_subito",        1.00,  0.45),
        Evidence("febre",                0.80,  0.50),  # alta mas nao extrema
        Evidence("dor_cabeca",           0.55,  0.15),
        Evidence("dor_muscular",         0.80,  0.50),
        Evidence("cansaco",              0.80,  0.40),
        Evidence("tosse_seca",           0.75,  0.35),
        Evidence("coriza",               0.50,  0.15),
        Evidence("congestao_nasal",      0.55,  0.15),
        Evidence("dor_garganta",         0.55,  0.20),
        Evidence("nausea_vomito",        0.50,  0.10),
        # Discriminador vs H1N1: intensidades extremas puxam para H1N1
        Evidence("febre",                1.00, -0.40),
        Evidence("dor_muscular",         1.00, -0.35),
        Evidence("cansaco",              1.00, -0.30),
        Evidence("nausea_vomito",        1.00, -0.30),
        # Contra-evidências
        Evidence("perda_olfato_paladar", 1.00, -0.70),
        Evidence("manchas_pele",         1.00, -0.70),
        Evidence("dor_atras_olhos",      1.00, -0.55),
        Evidence("dor_facial",           1.00, -0.50),
        Evidence("tosse_catarro",        1.00, -0.45),
        Evidence("falta_ar",             1.00, -0.45),
    ],

    # -------------------------------- H1N1 -------------------------------
    # Perfil: tudo exacerbado — febre > 39, dor muito intensa, cansaço
    # extremo, tosse seca intensa, náusea comum, pode ter falta de ar.
    "h1n1": [
        # Positivas — so disparam forte em intensidades muito altas
        Evidence("inicio_subito",        1.00,  0.50),
        Evidence("febre",                1.00,  0.65),  # febre muito alta
        Evidence("dor_cabeca",           0.80,  0.30),
        Evidence("dor_muscular",         1.00,  0.65),  # dor muito intensa
        Evidence("cansaco",              1.00,  0.60),  # cansaço extremo
        Evidence("tosse_seca",           1.00,  0.55),  # tosse seca intensa
        Evidence("dor_garganta",         0.55,  0.15),
        Evidence("falta_ar",             0.55,  0.40),
        Evidence("nausea_vomito",        0.80,  0.45),  # H1N1 tem vomito "Comum"
        # Discriminador vs gripe: febre/dor moderadas derrubam H1N1
        Evidence("febre",                0.55, -0.50),
        Evidence("dor_muscular",         0.55, -0.45),
        Evidence("cansaco",              0.55, -0.35),
        Evidence("febre",                0.80, -0.25),  # intenso (nao extremo)
        Evidence("dor_muscular",         0.80, -0.20),  # intenso (nao extremo)
        # Contra-evidências fortes para separar de dengue/COVID
        Evidence("perda_olfato_paladar", 1.00, -0.75),
        Evidence("manchas_pele",         1.00, -0.80),
        Evidence("dor_atras_olhos",      1.00, -0.70),  # marcador de dengue
        Evidence("dor_facial",           1.00, -0.50),
        Evidence("tosse_catarro",        1.00, -0.55),
        Evidence("coriza",               1.00, -0.40),
        Evidence("congestao_nasal",      1.00, -0.35),
    ],

    # ------------------------------ COVID-19 -----------------------------
    # Perfil: início variável, febre moderada, tosse seca persistente,
    # falta de ar, PERDA DE OLFATO/PALADAR (marcador forte).
    "covid": [
        # Marcador — presente eleva muito, ausente derruba
        Evidence("perda_olfato_paladar", 1.00,  0.85),  # marcador (presente)
        Evidence("perda_olfato_paladar", 0.00, -0.55),  # marcador (ausente)
        # Positivas (tabela: coriza/congestão/garganta "Comum" → 0.80)
        Evidence("falta_ar",             0.80,  0.50),
        Evidence("tosse_seca",           0.80,  0.45),
        Evidence("febre",                0.55,  0.25),
        Evidence("cansaco",              0.55,  0.20),
        Evidence("dor_muscular",         0.55,  0.20),
        Evidence("dor_cabeca",           0.55,  0.10),
        Evidence("coriza",               0.80,  0.15),
        Evidence("congestao_nasal",      0.80,  0.15),
        Evidence("dor_garganta",         0.80,  0.15),
        # Contra-evidências
        Evidence("manchas_pele",         1.00, -0.55),
        Evidence("dor_atras_olhos",      1.00, -0.60),  # marcador de dengue
        Evidence("dor_facial",           1.00, -0.45),
        Evidence("tosse_catarro",        1.00, -0.50),
    ],

    # ------------------------------- DENGUE ------------------------------
    # Perfil: início súbito, febre muito alta, DOR ATRÁS DOS OLHOS
    # (marcador) + MANCHAS NA PELE (marcador), dor muito intensa,
    # cansaço extremo, SEM sintomas respiratórios.
    "dengue": [
        # Marcadores — presentes elevam muito, dor atrás dos olhos ausente derruba
        Evidence("dor_atras_olhos",      1.00,  0.85),  # marcador (presente)
        Evidence("dor_atras_olhos",      0.00, -0.55),  # marcador (ausente)
        Evidence("manchas_pele",         0.85,  0.70),  # marcador
        # Positivas gerais
        Evidence("inicio_subito",        1.00,  0.45),
        Evidence("febre",                1.00,  0.50),
        Evidence("dor_cabeca",           1.00,  0.35),
        Evidence("dor_muscular",         1.00,  0.45),
        Evidence("cansaco",              1.00,  0.40),
        Evidence("nausea_vomito",        0.80,  0.35),
        # Contra-evidências: dengue quase não tem sintomas respiratórios
        Evidence("tosse_seca",           1.00, -0.70),
        Evidence("tosse_catarro",        1.00, -0.70),
        Evidence("coriza",               1.00, -0.65),
        Evidence("congestao_nasal",      1.00, -0.65),
        Evidence("dor_garganta",         1.00, -0.55),
        Evidence("falta_ar",             1.00, -0.50),
        Evidence("perda_olfato_paladar", 1.00, -0.65),
        Evidence("dor_facial",           1.00, -0.50),
    ],

    # ------------------------------ SINUSITE -----------------------------
    # Perfil: início gradual, sem febre, DOR FACIAL (marcador), coriza
    # muito comum, congestão intensa, tosse com catarro, duração longa.
    "sinusite": [
        # Marcador — dor facial é característica; ausência penaliza moderadamente
        Evidence("dor_facial",           0.90,  0.80),  # marcador (presente)
        Evidence("dor_facial",           0.00, -0.40),  # marcador (ausente)
        # Positivas
        Evidence("congestao_nasal",      0.90,  0.55),
        Evidence("coriza",               0.90,  0.45),
        Evidence("tosse_catarro",        0.75,  0.45),
        Evidence("dor_cabeca",           0.80,  0.35),
        Evidence("dor_atras_olhos",      0.55,  0.20),
        Evidence("perda_olfato_paladar", 0.55,  0.20),
        Evidence("dor_garganta",         0.55,  0.10),
        # Contra-evidências
        Evidence("inicio_subito",        1.00, -0.60),
        Evidence("febre",                1.00, -0.55),
        Evidence("dor_muscular",         1.00, -0.60),
        Evidence("manchas_pele",         1.00, -0.70),
        Evidence("tosse_seca",           1.00, -0.45),
        Evidence("falta_ar",             1.00, -0.40),
    ],
}


# --------------------------------------------------------------------
# 4) Recomendações associadas 
# --------------------------------------------------------------------
RECOMMENDATIONS: Dict[str, str] = {
    "resfriado": (
        "Repouso, hidratação e analgésicos comuns. Costuma resolver em "
        "3–5 dias. Procure atendimento se houver febre alta persistente."
    ),
    "gripe": (
        "Repouso, hidratação, antitérmicos. Em grupos de risco (idosos, "
        "gestantes, imunossuprimidos) considere avaliação médica para "
        "uso de antiviral nas primeiras 48h."
    ),
    "h1n1": (
        "Procure avaliação médica: quadro potencialmente grave. O uso "
        "precoce de oseltamivir pode ser indicado. Isolamento respiratório."
    ),
    "covid": (
        "Faça teste (RT-PCR ou antígeno) e isole-se. Procure emergência "
        "imediatamente em caso de falta de ar, dor no peito ou saturação "
        "de O₂ abaixo de 94%."
    ),
    "dengue": (
        "Hidratação oral abundante. Evite AAS e anti-inflamatórios. "
        "Procure emergência se houver dor abdominal intensa, sangramento, "
        "vômitos persistentes ou tontura — sinais de alarme."
    ),
    "sinusite": (
        "Lavagem nasal com soro fisiológico, analgésicos e hidratação. "
        "Se sintomas persistirem por 10 dias ou piora após melhora inicial, avaliação "
        "médica para possível antibiótico."
    ),
}
