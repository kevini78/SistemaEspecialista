"""
Testes de validacao do sistema especialista.

Para cada doenca da tabela, monta o perfil "classico" (exatamente
como descrito na tabela clinica de referencia) e verifica:
  1. Se a doenca correta fica em 1o lugar no ranking.
  2. Se a margem de confianca para a correta e razoavel.

Executar com:  python test_validation.py
"""

from knowledge_base import INTENSITY_LEVELS as L, DISEASES
from inference_engine import diagnose


# Helpers de leitura
A  = L["ausente"]
ML = L["muito_leve"]
LE = L["leve"]
MO = L["moderado"]
IN = L["intenso"]
MI = L["muito_intenso"]


# ---------------------------------------------------------------------
# Perfis "livro-texto" derivados diretamente da tabela
# ---------------------------------------------------------------------
# Convencoes de mapeamento dos termos da tabela:
#   Nao / Raro / Rara          -> ausente
#   Leve / Pouco comum         -> leve
#   Moderada/o, Comum, As vezes-> moderado
#   Alta, Intenso/a, Fortes    -> intenso
#   Muito alta, Muito intensa,
#   Extremo, Muito comum       -> muito_intenso
#
# "Inicio dos sintomas":
#   Gradual  -> inicio_subito = ausente
#   Variavel -> inicio_subito = moderado
#   Subito   -> inicio_subito = muito_intenso
#
# "Tosse" da tabela (agrupa seca/catarro):
#   Leve          -> tosse_seca=leve
#   Seca          -> tosse_seca=intenso
#   Seca intensa  -> tosse_seca=muito_intenso
#   Seca persist. -> tosse_seca=intenso
#   Rara          -> tosse_seca=ausente, tosse_catarro=ausente
#   Com catarro   -> tosse_catarro=intenso
#
# dor_facial so aparece na sinusite (coluna "Dor de cabeca: Intensa (face)")
# ---------------------------------------------------------------------

PROFILES = {
    "resfriado": {
        "inicio_subito":        A,   # Gradual
        "febre":                A,   # Rara
        "dor_cabeca":           LE,  # Leve
        "dor_atras_olhos":      A,   # Nao
        "dor_muscular":         LE,  # Leve
        "cansaco":              LE,  # Leve
        "tosse_seca":           LE,  # Leve
        "tosse_catarro":        A,
        "coriza":               IN,  # Comum
        "congestao_nasal":      IN,  # Comum
        "dor_garganta":         IN,  # Comum
        "falta_ar":             A,   # Raro
        "perda_olfato_paladar": A,   # Nao
        "manchas_pele":         A,   # Nao
        "nausea_vomito":        A,   # Raro
        "dor_facial":           A,
    },

    "gripe": {
        "inicio_subito":        MI,  # Subito
        "febre":                IN,  # Alta (38-39)
        "dor_cabeca":           MO,  # Moderada
        "dor_atras_olhos":      A,   # Raro
        "dor_muscular":         IN,  # Intensa
        "cansaco":              IN,  # Intenso
        "tosse_seca":           IN,  # Seca
        "tosse_catarro":        A,
        "coriza":               MO,  # As vezes
        "congestao_nasal":      MO,  # Moderada
        "dor_garganta":         MO,  # Moderada
        "falta_ar":             A,   # Raro
        "perda_olfato_paladar": A,   # Nao
        "manchas_pele":         A,   # Nao
        "nausea_vomito":        MO,  # As vezes
        "dor_facial":           A,
    },

    "h1n1": {
        "inicio_subito":        MI,  # Subito rapido
        "febre":                MI,  # Muito alta >39
        "dor_cabeca":           IN,  # Intensa
        "dor_atras_olhos":      A,   # Raro
        "dor_muscular":         MI,  # Muito intensa
        "cansaco":              MI,  # Extremo
        "tosse_seca":           MI,  # Seca intensa
        "tosse_catarro":        A,
        "coriza":               LE,  # Pouco comum
        "congestao_nasal":      LE,  # Leve
        "dor_garganta":         MO,  # Moderada
        "falta_ar":             MO,  # Pode ocorrer
        "perda_olfato_paladar": A,   # Nao
        "manchas_pele":         A,   # Nao
        "nausea_vomito":        IN,  # Comum
        "dor_facial":           A,
    },

    "covid": {
        "inicio_subito":        MO,  # Variavel
        "febre":                MO,  # Moderada
        "dor_cabeca":           MO,  # Moderada
        "dor_atras_olhos":      A,   # Raro
        "dor_muscular":         MO,  # Moderada
        "cansaco":              MO,  # Moderado
        "tosse_seca":           IN,  # Seca persistente
        "tosse_catarro":        A,
        "coriza":               IN,  # Comum
        "congestao_nasal":      IN,  # Comum
        "dor_garganta":         IN,  # Comum
        "falta_ar":             IN,  # Comum
        "perda_olfato_paladar": MI,  # Muito comum
        "manchas_pele":         A,   # Raro
        "nausea_vomito":        MO,  # As vezes
        "dor_facial":           A,
    },

    "dengue": {
        "inicio_subito":        MI,  # Subito
        "febre":                MI,  # Muito alta >39
        "dor_cabeca":           MI,  # Muito intensa
        "dor_atras_olhos":      MI,  # Muito comum
        "dor_muscular":         MI,  # Muito intensa
        "cansaco":              MI,  # Extremo
        "tosse_seca":           A,   # Rara
        "tosse_catarro":        A,
        "coriza":               A,   # Raro
        "congestao_nasal":      A,   # Raro
        "dor_garganta":         A,   # Raro
        "falta_ar":             A,   # Raro
        "perda_olfato_paladar": A,   # Nao
        "manchas_pele":         IN,  # Comum
        "nausea_vomito":        IN,  # Comum
        "dor_facial":           A,
    },

    "sinusite": {
        "inicio_subito":        A,   # Gradual
        "febre":                A,   # Rara
        "dor_cabeca":           IN,  # Intensa (face)
        "dor_atras_olhos":      IN,  # Comum
        "dor_muscular":         LE,  # Leve
        "cansaco":              MO,  # Moderado
        "tosse_seca":           A,
        "tosse_catarro":        IN,  # Com catarro
        "coriza":               MI,  # Muito comum
        "congestao_nasal":      IN,  # Intensa
        "dor_garganta":         MO,  # Moderada
        "falta_ar":             A,   # Raro
        "perda_olfato_paladar": MO,  # Pode ocorrer
        "manchas_pele":         A,   # Nao
        "nausea_vomito":        A,   # Raro
        "dor_facial":           IN,  # Pressao facial
    },
}


# ---------------------------------------------------------------------
# Cenarios de robustez: variacoes realistas dos perfis
# ---------------------------------------------------------------------
# Cada cenario descreve um caso plausivel que ainda assim deve apontar
# para a doenca correta (mesmo com sintomas faltando ou em intensidades
# ligeiramente diferentes do "livro-texto").
# ---------------------------------------------------------------------

SCENARIOS = [
    # --- Resfriado ---
    ("resfriado", "Resfriado classico (coriza forte, sem febre)", {
        "coriza": IN, "congestao_nasal": IN, "dor_garganta": MO,
    }),
    ("resfriado", "Resfriado leve com pouca dor de garganta", {
        "coriza": MO, "congestao_nasal": MO, "dor_garganta": LE,
        "cansaco": LE,
    }),

    # --- Gripe ---
    ("gripe", "Gripe classica", {
        "inicio_subito": MI, "febre": IN, "dor_muscular": IN,
        "cansaco": IN, "tosse_seca": IN, "dor_cabeca": MO,
    }),
    ("gripe", "Gripe com sintomas respiratorios moderados", {
        "inicio_subito": IN, "febre": IN, "dor_muscular": IN,
        "cansaco": MO, "tosse_seca": MO, "coriza": MO,
        "dor_garganta": MO,
    }),

    # --- H1N1 ---
    ("h1n1", "H1N1 grave (tudo no maximo)", {
        "inicio_subito": MI, "febre": MI, "dor_muscular": MI,
        "cansaco": MI, "tosse_seca": MI, "dor_cabeca": IN,
        "falta_ar": MO, "nausea_vomito": IN,
    }),

    # --- COVID-19 ---
    ("covid", "COVID com perda de olfato e tosse seca", {
        "febre": MO, "tosse_seca": IN, "falta_ar": MO,
        "perda_olfato_paladar": MI, "cansaco": MO,
    }),
    ("covid", "COVID sem febre mas com perda de olfato e falta de ar", {
        "tosse_seca": IN, "falta_ar": IN,
        "perda_olfato_paladar": MI, "cansaco": MO,
    }),

    # --- Dengue ---
    ("dengue", "Dengue com marcadores classicos", {
        "inicio_subito": MI, "febre": MI, "dor_cabeca": MI,
        "dor_atras_olhos": MI, "dor_muscular": MI, "cansaco": MI,
        "manchas_pele": IN,
    }),
    ("dengue", "Dengue sem manchas mas com dor atras dos olhos forte", {
        "febre": MI, "dor_cabeca": IN, "dor_atras_olhos": MI,
        "dor_muscular": IN, "cansaco": IN, "nausea_vomito": MO,
    }),

    # --- Sinusite ---
    ("sinusite", "Sinusite classica com dor facial", {
        "dor_facial": IN, "congestao_nasal": IN, "coriza": MI,
        "tosse_catarro": IN, "dor_cabeca": IN,
    }),
    ("sinusite", "Sinusite sem dor facial evidente", {
        "congestao_nasal": IN, "coriza": IN, "tosse_catarro": IN,
        "dor_cabeca": MO, "perda_olfato_paladar": MO,
    }),
]


def run():
    print("=" * 72)
    print("VALIDACAO 1/2: perfis 'livro-texto' extraidos da tabela")
    print("=" * 72)

    passed = 0
    total  = len(PROFILES)

    for expected_id, profile in PROFILES.items():
        results = diagnose(profile)
        top = results[0]
        runner_up = results[1]
        ok = top.disease_id == expected_id
        margin = top.cf - runner_up.cf

        status = "OK  " if ok else "FAIL"
        print(f"\n[{status}] Perfil de {DISEASES[expected_id]:20s}")
        print(f"       Top1: {top.disease_name:22s} CF={top.cf:+.3f}  ({top.confidence_pct:.1f}%)")
        print(f"       Top2: {runner_up.disease_name:22s} CF={runner_up.cf:+.3f}  (margem {margin:+.3f})")
        if not ok:
            print(f"       ESPERADO: {DISEASES[expected_id]}")
            print("       Ranking completo:")
            for r in results:
                mark = ">>" if r.disease_id == expected_id else "  "
                print(f"         {mark} {r.disease_name:22s} CF={r.cf:+.3f}")
        else:
            passed += 1

    print("\n" + "=" * 72)
    print("VALIDACAO 2/2: cenarios realistas com sintomas parciais")
    print("=" * 72)

    s_passed = 0
    s_total  = len(SCENARIOS)

    for expected_id, desc, obs in SCENARIOS:
        # Preenche sintomas nao informados como ausentes
        full_obs = {k: A for k in [
            "inicio_subito", "febre", "dor_cabeca", "dor_atras_olhos",
            "dor_muscular", "cansaco", "tosse_seca", "tosse_catarro",
            "coriza", "congestao_nasal", "dor_garganta", "falta_ar",
            "perda_olfato_paladar", "manchas_pele", "nausea_vomito",
            "dor_facial",
        ]}
        full_obs.update(obs)

        results = diagnose(full_obs)
        top = results[0]
        ok = top.disease_id == expected_id

        status = "OK  " if ok else "FAIL"
        print(f"\n[{status}] {desc}")
        print(f"       Esperado: {DISEASES[expected_id]}")
        print(f"       Top1:     {top.disease_name} ({top.confidence_pct:.1f}%)")
        if not ok:
            print("       Ranking:")
            for r in results[:3]:
                mark = ">>" if r.disease_id == expected_id else "  "
                print(f"         {mark} {r.disease_name:22s} CF={r.cf:+.3f}")
        else:
            s_passed += 1

    print("\n" + "=" * 72)
    print(f"Perfis classicos: {passed}/{total}")
    print(f"Cenarios realistas: {s_passed}/{s_total}")
    print(f"TOTAL: {passed + s_passed}/{total + s_total}")
    print("=" * 72)
    return passed == total and s_passed == s_total


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() else 1)
