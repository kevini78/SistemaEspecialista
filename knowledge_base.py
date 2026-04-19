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
# Conjuntos fuzzy triangulares simplificados (centróides).
# O usuário escolhe um rótulo linguístico; convertemos em grau [0,1].
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
        # Similaridade fuzzy entre o esperado e o observado
        return max(0.0, 1.0 - abs(self.expected - observed))


DISEASES: Dict[str, str] = {
    "resfriado": "Resfriado comum",
    "gripe":     "Gripe (Influenza)",
    "h1n1":      "Gripe H1N1",
    "covid":     "COVID-19",
    "dengue":    "Dengue",
    "sinusite":  "Sinusite",
}


# Convenção semântica (corrigida):
#
# POSITIVA:  Evidence(sintoma, esperado_alto, +peso)
#   - o sintoma favorece a hipótese quando observado próximo do esperado.
#
# CONTRA-EVIDÊNCIA: Evidence(sintoma, 1.00, -peso)
#   - só dispara penalidade quando o sintoma aparece com intensidade alta
#     (similaridade com 1.0). Quando o sintoma está ausente, a similaridade
#     é 0 e o CF fica 0 (não penaliza indevidamente).
#
# Essa convenção evita o bug de "penalizar por ausência" que existia antes.

RULES: Dict[str, List[Evidence]] = {
    # ----------------------------- RESFRIADO -----------------------------
    # Perfil: início gradual, sem febre, sintomas leves com predomínio de
    # coriza / congestão / dor de garganta.
    "resfriado": [
        # Positivas
        Evidence("febre",                0.00,  0.40),  # ausência apoia
        Evidence("dor_muscular",         0.33,  0.25),
        Evidence("cansaco",              0.33,  0.20),
        Evidence("tosse_seca",           0.33,  0.20),
        Evidence("coriza",               0.80,  0.60),
        Evidence("congestao_nasal",      0.80,  0.55),
        Evidence("dor_garganta",         0.70,  0.45),
        # Contra-evidências (só penalizam se sintoma intenso)
        Evidence("inicio_subito",        1.00, -0.45),
        Evidence("febre",                1.00, -0.60),
        Evidence("dor_cabeca",           1.00, -0.35),
        Evidence("dor_muscular",         1.00, -0.45),
        Evidence("cansaco",              1.00, -0.35),
        Evidence("dor_atras_olhos",      1.00, -0.45),
        Evidence("falta_ar",             1.00, -0.70),
        Evidence("perda_olfato_paladar", 1.00, -0.60),
        Evidence("manchas_pele",         1.00, -0.65),
        Evidence("dor_facial",           1.00, -0.35),
        Evidence("tosse_catarro",        1.00, -0.35),
    ],

    # ------------------------------- GRIPE -------------------------------
    # Perfil: início súbito, febre alta (38-39), dor muscular intensa,
    # cansaço intenso, tosse seca.
    "gripe": [
        # Positivas
        Evidence("inicio_subito",        1.00,  0.50),
        Evidence("febre",                0.80,  0.55),
        Evidence("dor_cabeca",           0.55,  0.30),
        Evidence("dor_muscular",         0.80,  0.55),
        Evidence("cansaco",              0.80,  0.50),
        Evidence("tosse_seca",           0.75,  0.45),
        Evidence("coriza",               0.50,  0.15),
        Evidence("congestao_nasal",      0.55,  0.15),
        Evidence("dor_garganta",         0.55,  0.20),
        Evidence("nausea_vomito",        0.50,  0.15),
        # Contra-evidências
        Evidence("perda_olfato_paladar", 1.00, -0.55),
        Evidence("manchas_pele",         1.00, -0.55),
        Evidence("dor_atras_olhos",      1.00, -0.35),
        Evidence("dor_facial",           1.00, -0.35),
        Evidence("tosse_catarro",        1.00, -0.35),
        Evidence("falta_ar",             1.00, -0.30),
    ],

    # -------------------------------- H1N1 -------------------------------
    # Perfil: tudo exacerbado — febre > 39, dor muito intensa, cansaço
    # extremo, tosse seca intensa, náusea comum, pode ter falta de ar.
    "h1n1": [
        # Positivas (intensidades mais altas que gripe comum)
        Evidence("inicio_subito",        1.00,  0.55),
        Evidence("febre",                1.00,  0.60),
        Evidence("dor_cabeca",           0.80,  0.40),
        Evidence("dor_muscular",         1.00,  0.60),
        Evidence("cansaco",              1.00,  0.55),
        Evidence("tosse_seca",           1.00,  0.55),
        Evidence("dor_garganta",         0.55,  0.20),
        Evidence("falta_ar",             0.55,  0.30),
        Evidence("nausea_vomito",        0.80,  0.30),
        # Contra-evidências
        Evidence("perda_olfato_paladar", 1.00, -0.55),
        Evidence("manchas_pele",         1.00, -0.55),
        Evidence("dor_atras_olhos",      1.00, -0.35),
        Evidence("dor_facial",           1.00, -0.35),
        Evidence("tosse_catarro",        1.00, -0.40),
        Evidence("coriza",               1.00, -0.25),
        Evidence("congestao_nasal",      1.00, -0.20),
    ],

    # ------------------------------ COVID-19 -----------------------------
    # Perfil: início variável, febre moderada, tosse seca persistente,
    # falta de ar, PERDA DE OLFATO/PALADAR (marcador forte).
    "covid": [
        # Positivas
        Evidence("perda_olfato_paladar", 1.00,  0.85),  # marcador
        Evidence("falta_ar",             0.80,  0.55),
        Evidence("tosse_seca",           0.80,  0.50),
        Evidence("febre",                0.55,  0.30),
        Evidence("cansaco",              0.55,  0.25),
        Evidence("dor_muscular",         0.55,  0.25),
        Evidence("dor_cabeca",           0.55,  0.20),
        Evidence("coriza",               0.55,  0.10),
        Evidence("congestao_nasal",      0.55,  0.10),
        Evidence("dor_garganta",         0.55,  0.15),
        # Contra-evidências
        Evidence("manchas_pele",         1.00, -0.45),
        Evidence("dor_atras_olhos",      1.00, -0.40),
        Evidence("dor_facial",           1.00, -0.35),
        Evidence("tosse_catarro",        1.00, -0.40),
    ],

    # ------------------------------- DENGUE ------------------------------
    # Perfil: início súbito, febre muito alta, DOR ATRÁS DOS OLHOS
    # (marcador) + MANCHAS NA PELE (marcador), dor muito intensa,
    # cansaço extremo, SEM sintomas respiratórios.
    "dengue": [
        # Positivas (marcadores primeiro)
        Evidence("dor_atras_olhos",      1.00,  0.85),  # marcador
        Evidence("manchas_pele",         0.85,  0.70),  # marcador
        Evidence("inicio_subito",        1.00,  0.50),
        Evidence("febre",                1.00,  0.55),
        Evidence("dor_cabeca",           1.00,  0.55),
        Evidence("dor_muscular",         1.00,  0.55),
        Evidence("cansaco",              1.00,  0.50),
        Evidence("nausea_vomito",        0.80,  0.35),
        # Contra-evidências: dengue quase não tem sintomas respiratórios
        Evidence("tosse_seca",           1.00, -0.60),
        Evidence("tosse_catarro",        1.00, -0.60),
        Evidence("coriza",               1.00, -0.55),
        Evidence("congestao_nasal",      1.00, -0.55),
        Evidence("dor_garganta",         1.00, -0.45),
        Evidence("falta_ar",             1.00, -0.40),
        Evidence("perda_olfato_paladar", 1.00, -0.55),
        Evidence("dor_facial",           1.00, -0.40),
    ],

    # ------------------------------ SINUSITE -----------------------------
    # Perfil: início gradual, sem febre, DOR FACIAL (marcador), coriza
    # muito comum, congestão intensa, tosse com catarro, duração longa.
    "sinusite": [
        # Positivas
        Evidence("dor_facial",           0.90,  0.80),  # marcador
        Evidence("congestao_nasal",      0.90,  0.60),
        Evidence("coriza",               0.90,  0.50),
        Evidence("tosse_catarro",        0.75,  0.50),
        Evidence("dor_cabeca",           0.80,  0.40),
        Evidence("dor_atras_olhos",      0.55,  0.25),
        Evidence("perda_olfato_paladar", 0.55,  0.25),
        Evidence("dor_garganta",         0.55,  0.15),
        Evidence("febre",                0.00,  0.20),  # tipicamente ausente
        # Contra-evidências
        Evidence("inicio_subito",        1.00, -0.50),
        Evidence("febre",                1.00, -0.45),
        Evidence("dor_muscular",         1.00, -0.50),
        Evidence("manchas_pele",         1.00, -0.55),
        Evidence("tosse_seca",           1.00, -0.35),
        Evidence("falta_ar",             1.00, -0.30),
    ],
}


# --------------------------------------------------------------------
# 4) Recomendações associadas (explicações para o usuário)
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
        "Se sintomas > 10 dias ou piora após melhora inicial, avaliação "
        "médica para possível antibiótico."
    ),
}
