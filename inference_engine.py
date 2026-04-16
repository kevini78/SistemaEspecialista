"""
Motor de inferência por encadeamento direto (forward chaining)
com combinação de Fatores de Certeza (MYCIN).

Para cada doença (hipótese) avaliamos todas as regras da base de
conhecimento. A evidência observada pelo usuário (intensidade fuzzy
de cada sintoma) dispara cada regra com um CF proporcional à
similaridade entre a intensidade esperada e a observada.

Combinação incremental de CFs (MYCIN):
    se cf1 >= 0 e cf2 >= 0:  cf = cf1 + cf2*(1 - cf1)
    se cf1 <= 0 e cf2 <= 0:  cf = cf1 + cf2*(1 + cf1)
    caso contrário:           cf = (cf1 + cf2) / (1 - min(|cf1|,|cf2|))
"""

from dataclasses import dataclass, field
from typing import Dict, List

from knowledge_base import DISEASES, RULES, Evidence


@dataclass
class FiredRule:
    """Registro de uma regra disparada, usado para explicação."""
    symptom: str
    expected: float
    observed: float
    similarity: float
    weight: float
    cf: float


@dataclass
class DiagnosisResult:
    disease_id: str
    disease_name: str
    cf: float                         # fator de certeza final [-1, 1]
    confidence_pct: float             # 0–100 %, derivado de max(0, cf)
    fired_rules: List[FiredRule] = field(default_factory=list)

    @property
    def positive_rules(self) -> List[FiredRule]:
        return sorted(
            [r for r in self.fired_rules if r.cf > 0.01],
            key=lambda r: -r.cf,
        )

    @property
    def negative_rules(self) -> List[FiredRule]:
        return sorted(
            [r for r in self.fired_rules if r.cf < -0.01],
            key=lambda r: r.cf,
        )


# ---------------------------------------------------------------------
# Combinação de fatores de certeza — fórmulas MYCIN
# ---------------------------------------------------------------------
def combine_cf(cf1: float, cf2: float) -> float:
    if cf1 >= 0 and cf2 >= 0:
        return cf1 + cf2 * (1 - cf1)
    if cf1 <= 0 and cf2 <= 0:
        return cf1 + cf2 * (1 + cf1)
    return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))


# ---------------------------------------------------------------------
# Avaliação de uma hipótese (doença) dadas as observações fuzzy
# ---------------------------------------------------------------------
def _evaluate_disease(
    disease_id: str,
    observations: Dict[str, float],
) -> DiagnosisResult:
    cf_total = 0.0
    fired: List[FiredRule] = []

    for ev in RULES[disease_id]:
        observed = observations.get(ev.symptom, 0.0)

        # Se o usuário não marcou o sintoma (0.0) e a evidência é
        # positiva com esperado alto, a similaridade cai e o CF será
        # baixo — comportamento desejado.
        sim = ev.similarity(observed)
        cf_rule = ev.weight * sim

        # Regras com CF negligenciável não disparam.
        if abs(cf_rule) < 0.02:
            continue

        cf_total = combine_cf(cf_total, cf_rule)
        fired.append(FiredRule(
            symptom=ev.symptom,
            expected=ev.expected,
            observed=observed,
            similarity=sim,
            weight=ev.weight,
            cf=cf_rule,
        ))

    cf_total = max(-1.0, min(1.0, cf_total))
    return DiagnosisResult(
        disease_id=disease_id,
        disease_name=DISEASES[disease_id],
        cf=cf_total,
        confidence_pct=round(max(0.0, cf_total) * 100, 1),
        fired_rules=fired,
    )


# ---------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------
def diagnose(observations: Dict[str, float]) -> List[DiagnosisResult]:
    """
    Recebe um dicionário {sintoma_id: intensidade_fuzzy [0..1]} e
    retorna a lista de diagnósticos ordenada do mais provável para o
    menos provável.
    """
    results = [_evaluate_disease(d, observations) for d in DISEASES]
    results.sort(key=lambda r: -r.cf)
    return results
