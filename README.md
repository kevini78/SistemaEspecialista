# Sistema Especialista — Diagnóstico Respiratório

Protótipo em **Python + Streamlit** que realiza diagnóstico diferencial
entre **Resfriado, Gripe, H1N1, COVID-19, Dengue e Sinusite**, usando
regras de produção com **Fatores de Certeza (MYCIN)** e **lógica fuzzy**
para tratamento de incertezas.

> ⚠️ Uso educacional — não substitui avaliação médica.

---

## Tabela clínica de referência

| Sintoma / Critério | Resfriado | Gripe (Influenza) | H1N1 | COVID-19 | Dengue | Sinusite |
|---|---|---|---|---|---|---|
| Início dos sintomas | Gradual | Súbito | Súbito (rápido) | Variável | Súbito | Gradual |
| Febre | Rara | Alta (38–39 °C) | Muito alta (>39 °C) | Moderada | Muito alta (>39 °C) | Rara |
| Dor de cabeça | Leve | Moderada | Intensa | Moderada | Muito intensa | Intensa (face) |
| Dor atrás dos olhos | Não | Raro | Raro | Raro | Muito comum | Comum |
| Dor muscular | Leve | Intensa | Muito intensa | Moderada | Muito intensa | Leve |
| Cansaço / fadiga | Leve | Intenso | Extremo | Moderado | Extremo | Moderado |
| Tosse | Leve | Seca | Seca intensa | Seca persistente | Rara | Com catarro |
| Coriza | Comum | Às vezes | Pouco comum | Comum | Raro | Muito comum |
| Congestão nasal | Comum | Moderada | Leve | Comum | Raro | Intensa |
| Dor de garganta | Comum | Moderada | Moderada | Comum | Raro | Moderada |
| Falta de ar | Raro | Raro | Pode ocorrer | Comum | Raro | Raro |
| Perda de olfato/paladar | Não | Não | Não | Muito comum | Não | Pode ocorrer |
| Manchas na pele | Não | Não | Não | Raro | Comum | Não |
| Sintomas respiratórios | Leves | Fortes | Muito fortes | Fortes | Quase ausentes | Fortes |
| Náusea / vômito | Raro | Às vezes | Comum | Às vezes | Comum | Raro |
| Duração média | 3–5 dias | 7–10 dias | 7–14 dias | 5–14 dias | 5–10 dias | >10 dias |

---

## Como rodar

Pré-requisitos: **Python 3.10+**.

```bash
pip install -r requirements.txt
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`.
