"""
Suite de validacao do sistema especialista.

Roda tres baterias de testes:

  1. PERFIS CLASSICOS: para cada doenca, monta o perfil exato descrito
     na tabela de referencia e verifica que a doenca correta fica em
     1o lugar COM MARGEM razoavel sobre o 2o colocado.

  2. CENARIOS REALISTAS: casos com sintomas parciais ou intensidades
     ligeiramente diferentes do livro-texto.

  3. CASOS LIMITE: perfis que devem ser classificados como
     inconclusivos (nenhum sintoma, so sintomas inespecificos).

Uso: python test_validation.py
"""

from knowledge_base import INTENSITY_LEVELS as L, SYMPTOMS, DISEASES
from inference_engine import diagnose


# Atalhos de intensidade
A  = L["ausente"]
ML = L["muito_leve"]
LE = L["leve"]
MO = L["moderado"]
IN = L["intenso"]
MI = L["muito_intenso"]


# Todos os sintomas inicializam em 0 por padrao
def _obs(**overrides):
    base = {k: A for k in SYMPTOMS}
    base.update(overrides)
    return base


# =====================================================================
# BATERIA 1: perfis livro-texto da tabela
# =====================================================================
# Mapeamento dos termos da tabela para intensidades:
#   Nao / Raro / Rara              -> ausente
#   Leve / Pouco comum             -> leve
#   Moderada/o, Comum, As vezes    -> moderado
#   Alta, Intensa/o                -> intenso
#   Muito alta, Muito intensa,
#   Extremo, Muito comum           -> muito_intenso
# Inicio dos sintomas:
#   Gradual  -> inicio_subito=0
#   Variavel -> inicio_subito=moderado
#   Subito   -> inicio_subito=muito_intenso

PROFILES = {
    "resfriado": _obs(
        inicio_subito=A, febre=A,
        dor_cabeca=LE, dor_atras_olhos=A,
        dor_muscular=LE, cansaco=LE,
        tosse_seca=LE, tosse_catarro=A,
        coriza=MO, congestao_nasal=MO,  # "Comum"
        dor_garganta=MO,                  # "Comum"
        falta_ar=A, perda_olfato_paladar=A,
        manchas_pele=A, nausea_vomito=A, dor_facial=A,
    ),
    "gripe": _obs(
        inicio_subito=MI, febre=IN,
        dor_cabeca=MO, dor_atras_olhos=A,
        dor_muscular=IN, cansaco=IN,
        tosse_seca=IN, tosse_catarro=A,
        coriza=MO, congestao_nasal=MO, dor_garganta=MO,
        falta_ar=A, perda_olfato_paladar=A,
        manchas_pele=A, nausea_vomito=MO, dor_facial=A,
    ),
    "h1n1": _obs(
        inicio_subito=MI, febre=MI,
        dor_cabeca=IN, dor_atras_olhos=A,
        dor_muscular=MI, cansaco=MI,
        tosse_seca=MI, tosse_catarro=A,
        coriza=LE, congestao_nasal=LE, dor_garganta=MO,
        falta_ar=MO, perda_olfato_paladar=A,
        manchas_pele=A, nausea_vomito=IN, dor_facial=A,
    ),
    "covid": _obs(
        inicio_subito=MO, febre=MO,
        dor_cabeca=MO, dor_atras_olhos=A,
        dor_muscular=MO, cansaco=MO,
        tosse_seca=IN, tosse_catarro=A,
        coriza=MO, congestao_nasal=MO, dor_garganta=MO,
        falta_ar=IN, perda_olfato_paladar=MI,
        manchas_pele=A, nausea_vomito=MO, dor_facial=A,
    ),
    "dengue": _obs(
        inicio_subito=MI, febre=MI,
        dor_cabeca=MI, dor_atras_olhos=MI,
        dor_muscular=MI, cansaco=MI,
        tosse_seca=A, tosse_catarro=A,
        coriza=A, congestao_nasal=A, dor_garganta=A,
        falta_ar=A, perda_olfato_paladar=A,
        manchas_pele=IN, nausea_vomito=IN, dor_facial=A,
    ),
    "sinusite": _obs(
        inicio_subito=A, febre=A,
        dor_cabeca=IN, dor_atras_olhos=IN,
        dor_muscular=LE, cansaco=MO,
        tosse_seca=A, tosse_catarro=IN,
        coriza=MI, congestao_nasal=IN, dor_garganta=MO,
        falta_ar=A, perda_olfato_paladar=MO,
        manchas_pele=A, nausea_vomito=A, dor_facial=IN,
    ),
}


# =====================================================================
# BATERIA 2: variacoes realistas
# =====================================================================

SCENARIOS = [
    # --- Resfriado ---
    ("resfriado", "Resfriado classico: coriza forte, sem febre",
     _obs(coriza=IN, congestao_nasal=IN, dor_garganta=MO)),
    ("resfriado", "Resfriado leve",
     _obs(coriza=MO, congestao_nasal=MO, dor_garganta=LE, cansaco=LE)),
    ("resfriado", "Resfriado com tosse leve e garganta",
     _obs(coriza=MO, dor_garganta=MO, tosse_seca=LE, cansaco=LE)),

    # --- Gripe ---
    ("gripe", "Gripe classica",
     _obs(inicio_subito=MI, febre=IN, dor_muscular=IN,
          cansaco=IN, tosse_seca=IN, dor_cabeca=MO)),
    ("gripe", "Gripe moderada",
     _obs(inicio_subito=IN, febre=IN, dor_muscular=MO,
          cansaco=MO, tosse_seca=MO, coriza=MO)),
    ("gripe", "Gripe com algumas nauseas",
     _obs(inicio_subito=MI, febre=IN, dor_muscular=IN, cansaco=IN,
          tosse_seca=IN, nausea_vomito=MO, dor_cabeca=MO)),

    # --- H1N1 ---
    ("h1n1", "H1N1 grave",
     _obs(inicio_subito=MI, febre=MI, dor_muscular=MI,
          cansaco=MI, tosse_seca=MI, dor_cabeca=IN,
          falta_ar=MO, nausea_vomito=IN)),
    ("h1n1", "H1N1 com falta de ar",
     _obs(inicio_subito=MI, febre=MI, dor_muscular=MI,
          cansaco=MI, tosse_seca=IN, falta_ar=IN,
          nausea_vomito=IN)),

    # --- COVID ---
    ("covid", "COVID com perda de olfato",
     _obs(febre=MO, tosse_seca=IN, falta_ar=MO,
          perda_olfato_paladar=MI, cansaco=MO)),
    ("covid", "COVID com sintomas respiratorios fortes",
     _obs(tosse_seca=IN, falta_ar=IN, perda_olfato_paladar=MI,
          cansaco=MO, febre=MO, dor_garganta=MO)),
    ("covid", "COVID com dor de garganta, coriza e perda de olfato",
     _obs(coriza=MO, congestao_nasal=MO, dor_garganta=MO,
          tosse_seca=IN, perda_olfato_paladar=MI, cansaco=MO)),

    # --- Dengue ---
    ("dengue", "Dengue com marcadores completos",
     _obs(inicio_subito=MI, febre=MI, dor_cabeca=MI,
          dor_atras_olhos=MI, dor_muscular=MI, cansaco=MI,
          manchas_pele=IN)),
    ("dengue", "Dengue sem manchas mas com dor retroorbital",
     _obs(febre=MI, dor_cabeca=IN, dor_atras_olhos=MI,
          dor_muscular=IN, cansaco=IN, nausea_vomito=MO)),
    ("dengue", "Dengue com apenas dor atras dos olhos e febre alta",
     _obs(febre=MI, dor_atras_olhos=IN, dor_muscular=IN,
          cansaco=IN, manchas_pele=MO)),

    # --- Sinusite ---
    ("sinusite", "Sinusite classica com dor facial",
     _obs(dor_facial=IN, congestao_nasal=IN, coriza=MI,
          tosse_catarro=IN, dor_cabeca=IN)),
    ("sinusite", "Sinusite sem dor facial evidente",
     _obs(congestao_nasal=IN, coriza=IN, tosse_catarro=IN,
          dor_cabeca=MO, perda_olfato_paladar=MO)),
    ("sinusite", "Sinusite com dor de cabeca frontal",
     _obs(dor_facial=IN, dor_cabeca=IN, congestao_nasal=IN,
          coriza=IN, tosse_catarro=MO)),
]


# =====================================================================
# BATERIA 3: casos limite
# =====================================================================

EDGE_CASES = [
    ("Nenhum sintoma informado", _obs(),
     "inconclusive"),
    ("Apenas cansaco leve (inespecifico)",
     _obs(cansaco=LE),
     "inconclusive"),
    ("Apenas dor de cabeca moderada (inespecifico)",
     _obs(dor_cabeca=MO),
     "inconclusive"),
]


# =====================================================================
# Execucao
# =====================================================================

MIN_MARGIN_CLASSIC = 0.08   # margem minima esperada para perfil livro-texto
MIN_MARGIN_SCENARIO = 0.03  # mais permissivo para variacoes


def _run_classic():
    print("=" * 72)
    print("BATERIA 1 — perfis classicos (tabela livro-texto)")
    print("=" * 72)
    passed = 0
    for expected_id, profile in PROFILES.items():
        results = diagnose(profile)
        top, runner_up = results[0], results[1]
        margin = top.cf - runner_up.cf
        ok = (top.disease_id == expected_id) and (margin >= MIN_MARGIN_CLASSIC)
        mark = "OK  " if ok else "FAIL"
        print(f"\n[{mark}] {DISEASES[expected_id]:22s}")
        print(f"       Top1: {top.disease_name:22s} {top.confidence_pct:5.1f}%")
        print(f"       Top2: {runner_up.disease_name:22s} {runner_up.confidence_pct:5.1f}%  "
              f"(margem {margin:+.3f})")
        if not ok:
            print(f"       ESPERADO: {DISEASES[expected_id]} (margem minima {MIN_MARGIN_CLASSIC})")
            for r in results:
                m = ">>" if r.disease_id == expected_id else "  "
                print(f"         {m} {r.disease_name:22s} CF={r.cf:+.3f}")
        if ok:
            passed += 1
    return passed, len(PROFILES)


def _run_scenarios():
    print("\n" + "=" * 72)
    print("BATERIA 2 — cenarios realistas com sintomas parciais")
    print("=" * 72)
    passed = 0
    for expected_id, desc, obs in SCENARIOS:
        results = diagnose(obs)
        top, runner_up = results[0], results[1]
        margin = top.cf - runner_up.cf
        ok = (top.disease_id == expected_id) and (margin >= MIN_MARGIN_SCENARIO)
        mark = "OK  " if ok else "FAIL"
        print(f"\n[{mark}] {desc}")
        print(f"       Esperado: {DISEASES[expected_id]}")
        print(f"       Top1: {top.disease_name} ({top.confidence_pct:.1f}%) "
              f"| Top2: {runner_up.disease_name} ({runner_up.confidence_pct:.1f}%) "
              f"| margem {margin:+.3f}")
        if not ok:
            for r in results[:3]:
                m = ">>" if r.disease_id == expected_id else "  "
                print(f"         {m} {r.disease_name:22s} CF={r.cf:+.3f}")
        if ok:
            passed += 1
    return passed, len(SCENARIOS)


def _run_edge():
    print("\n" + "=" * 72)
    print("BATERIA 3 — casos limite (devem ficar inconclusivos)")
    print("=" * 72)
    passed = 0
    for desc, obs, mode in EDGE_CASES:
        results = diagnose(obs)
        top = results[0]
        # Consideramos "inconclusivo" quando a confianca do top fica baixa
        ok = top.confidence_pct < 30
        mark = "OK  " if ok else "FAIL"
        print(f"\n[{mark}] {desc}")
        print(f"       Top1: {top.disease_name} ({top.confidence_pct:.1f}%)")
        if ok:
            passed += 1
    return passed, len(EDGE_CASES)


def main():
    p1, t1 = _run_classic()
    p2, t2 = _run_scenarios()
    p3, t3 = _run_edge()

    print("\n" + "=" * 72)
    print("RESUMO")
    print("=" * 72)
    print(f"  Perfis classicos:   {p1}/{t1}")
    print(f"  Cenarios realistas: {p2}/{t2}")
    print(f"  Casos limite:       {p3}/{t3}")
    print(f"  TOTAL:              {p1+p2+p3}/{t1+t2+t3}")
    print("=" * 72)
    return p1 == t1 and p2 == t2 and p3 == t3


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
