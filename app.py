"""
Interface Streamlit do Sistema Especialista de Diagnóstico Respiratório.

Visual inspirado no projeto "health-compass" (paleta sóbria, cards com
bordas suaves e badges por nível de confiança), porém construído com
outra pilha tecnológica (Python + Streamlit).
"""

from __future__ import annotations

import streamlit as st

from knowledge_base import (
    INTENSITY_LABELS,
    INTENSITY_LEVELS,
    RECOMMENDATIONS,
    SYMPTOMS,
)
from inference_engine import diagnose


# ---------------------------------------------------------------------
# Configuração de página + tema visual
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema Especialista — Diagnóstico Respiratório",
    page_icon="🩺",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    :root {
        --primary: #0f172a;
        --accent:  #2563eb;
        --muted:   #64748b;
        --border:  #e2e8f0;
    }
    .block-container { padding-top: 1.2rem; max-width: 1100px; }
    h1, h2, h3 { color: var(--primary); letter-spacing: -0.01em; }

    .hero {
        background: linear-gradient(135deg, #eff6ff 0%, #ecfeff 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0 0 .25rem 0; font-size: 1.6rem; }
    .hero p  { margin: 0; color: var(--muted); }

    .sym-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: .75rem .9rem .2rem .9rem;
        margin-bottom: .6rem;
    }
    .sym-label { font-weight: 600; color: var(--primary); margin-bottom: .15rem; }

    /* Botões de rádio horizontais parecendo "pills" */
    div[role="radiogroup"] { gap: .35rem !important; flex-wrap: wrap; }
    div[role="radiogroup"] > label {
        background: #f1f5f9;
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: .2rem .7rem !important;
        margin: 0 !important;
        cursor: pointer;
        transition: all .15s ease;
    }
    div[role="radiogroup"] > label:hover { background: #e2e8f0; }
    div[role="radiogroup"] > label[data-checked="true"],
    div[role="radiogroup"] > label:has(input:checked) {
        background: #dbeafe;
        border-color: #2563eb;
        color: #1d4ed8;
        font-weight: 600;
    }
    div[role="radiogroup"] > label > div:first-child { display: none; }

    .main-result {
        background: linear-gradient(135deg, #ecfdf5 0%, #eff6ff 100%);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .main-result.warn  { background: linear-gradient(135deg,#fff7ed,#fef9c3); border-color:#fcd34d; }
    .main-result.low   { background: #f8fafc; border-color: var(--border); }
    .main-result h2 { margin: 0 0 .3rem 0; font-size: 1.5rem; }
    .main-result .confidence {
        display: inline-block; padding: .25rem .75rem; border-radius: 999px;
        background: rgba(15,23,42,.08); font-weight: 600; font-size: .9rem;
    }
    .main-result p { margin: .6rem 0 0 0; color: #334155; }

    .alt-card {
        background: #ffffff; border: 1px solid var(--border);
        border-radius: 12px; padding: .75rem 1rem; margin-bottom: .5rem;
        display: flex; align-items: center; justify-content: space-between;
    }
    .alt-name { color: var(--primary); font-weight: 500; }
    .alt-pct  { color: var(--muted); font-size: .9rem; }

    .disclaimer {
        background: #fef2f2; border: 1px solid #fecaca; color: #991b1b;
        padding: .7rem .9rem; border-radius: 12px; font-size: .88rem;
        margin-bottom: 1rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🩺 Sistema Especialista — Diagnóstico Respiratório</h1>
        <p>Regras de produção + Fatores de Certeza (MYCIN) + Lógica Fuzzy —
        triagem entre Resfriado, Gripe, H1N1, COVID-19, Dengue e Sinusite.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="disclaimer">⚠️ <b>Uso educacional.</b> Este protótipo '
    'não substitui avaliação médica profissional.</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Entrada: intensidade de cada sintoma (click-based, não arrastar)
# ---------------------------------------------------------------------
st.subheader("Informe a intensidade de cada sintoma")
st.caption("Clique no nível correspondente. Se não apresentar, deixe em **Ausente**.")

level_keys = list(INTENSITY_LEVELS.keys())
observations: dict[str, float] = {}

items = list(SYMPTOMS.items())
col1, col2 = st.columns(2, gap="medium")
half = (len(items) + 1) // 2

def render_symptom(container, sid: str, label: str):
    with container:
        st.markdown(
            f'<div class="sym-label">{label}</div>',
            unsafe_allow_html=True,
        )
        choice = st.radio(
            label,
            options=level_keys,
            index=0,
            horizontal=True,
            format_func=lambda k: INTENSITY_LABELS[k],
            key=f"sym_{sid}",
            label_visibility="collapsed",
        )
        observations[sid] = INTENSITY_LEVELS[choice]
        st.write("")

for sid, label in items[:half]:
    render_symptom(col1, sid, label)
for sid, label in items[half:]:
    render_symptom(col2, sid, label)


# ---------------------------------------------------------------------
# Botão e resultado final
# ---------------------------------------------------------------------
st.write("")
run = st.button("🔎 Obter diagnóstico", type="primary", use_container_width=True)

if run:
    results = diagnose(observations)
    top = results[0]

    # Se nenhuma hipótese passa de um mínimo, informamos inconclusivo
    if top.confidence_pct < 20:
        st.markdown(
            """
            <div class="main-result low">
                <h2>Diagnóstico inconclusivo</h2>
                <span class="confidence">Confiança insuficiente</span>
                <p>Os sintomas informados não são suficientes para
                sugerir uma hipótese com confiança razoável. Reveja as
                intensidades ou procure avaliação médica.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        if top.confidence_pct >= 65:
            css_class, nivel = "", "Alta confiança"
        elif top.confidence_pct >= 40:
            css_class, nivel = "warn", "Confiança moderada"
        else:
            css_class, nivel = "low", "Baixa confiança"

        st.markdown(
            f"""
            <div class="main-result {css_class}">
                <h2>🎯 Diagnóstico mais provável: <b>{top.disease_name}</b></h2>
                <span class="confidence">{nivel} · {top.confidence_pct:.1f}%</span>
                <p><b>Recomendação:</b> {RECOMMENDATIONS[top.disease_id]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Hipóteses alternativas (apenas as com algum grau de certeza)
        others = [r for r in results[1:] if r.confidence_pct >= 10]
        if others:
            st.markdown("#### Outras hipóteses consideradas")
            for r in others:
                st.markdown(
                    f"""
                    <div class="alt-card">
                        <span class="alt-name">{r.disease_name}</span>
                        <span class="alt-pct">{r.confidence_pct:.1f}%</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------
# Rodapé explicativo (documentação in-app)
# ---------------------------------------------------------------------
with st.expander("ℹ️ Sobre o sistema (fundamentação teórica)"):
    st.markdown(
        """
- **Representação do conhecimento:** regras de produção ponderadas
  (`SE sintoma tem intensidade X ENTÃO evidência para doença D`).
- **Resolução de problemas:** encadeamento direto (*forward chaining*)
  avaliando todas as hipóteses a partir dos sintomas informados.
- **Tratamento de incerteza:** (1) **lógica fuzzy** para os rótulos de
  intensidade (ausente → muito intenso); (2) **Fatores de Certeza**
  no estilo MYCIN para combinar as evidências.
- **Aprendizagem de máquina (perspectiva):** os pesos das regras
  poderiam ser aprendidos por indução simbólica ou regressão
  numérica a partir de casos rotulados.
        """
    )
