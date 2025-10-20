import streamlit as st
import google.generativeai as genai
import os

# ---------- Guardrails ----------
def sanitize_text(s: str, max_len=300):
    s = (s or "").strip().replace("\n", " ")
    return s[:max_len]

def validate_numbers(budget, cpr):
    try:
        budget = float(budget)
        cpr = float(cpr)
    except Exception:
        raise ValueError("Orçamento e CPR precisam ser números (ex.: 60 e 3).")
    if budget <= 0 or cpr <= 0:
        raise ValueError("Orçamento e CPR devem ser > 0.")
    if budget > 1e6 or cpr > 1e5:
        raise ValueError("Valores muito altos para a aula. Revise.")
    return budget, cpr

# Prompt mais conciso e com limites um pouco mais altos (legendas e total)
PROMPT_TEMPLATE = """Você é uma assistente de marketing didática.

Tarefa: gerar 3 IDEIAS de post e 2 LEGENDAS curtas por IDEIA.
Regras:
- Não prometa resultados garantidos; seja clara e específica; sem jargões.
- Cada IDEIA: título curto + ângulo (1 linha).
- Cada LEGENDA: ≤ 160 caracteres e com CTA simples.
- Saída TOTAL concisa (≈ 250–300 palavras).

Contexto:
- Tema/Nicho: {topic}
- Público: {audience}
- Oferta/Ângulo: {offer}
- Tom de voz: {tone}

Formato de saída (exato):
1) IDEIAS
1. ...
2. ...
3. ...
2) LEGENDAS
Para IDEIA 1:
- ...
- ...
Para IDEIA 2:
- ...
- ...
Para IDEIA 3:
- ...
- ...
"""

def build_prompt(topic, audience, offer, tone):
    return PROMPT_TEMPLATE.format(
        topic=sanitize_text(topic),
        audience=sanitize_text(audience),
        offer=sanitize_text(offer),
        tone=sanitize_text(tone),
    )

def safe_response_text(response):
    # tenta usar .text; se não vier, extrai manualmente
    try:
        txt = (response.text or "").strip()
        if txt:
            return txt
    except Exception:
        pass
    try:
        cand = response.candidates[0]
        parts = getattr(cand.content, "parts", []) or []
        texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", "")]
        if texts:
            return "\n".join(texts).strip()
        fr = getattr(cand, "finish_reason", "UNKNOWN")
        return f"[Sem texto na resposta; finish_reason={fr}]"
    except Exception:
        return "[Sem texto e sem candidates]"

def _try_generate(model, prompt):
    # 1ª tentativa
    resp = model.generate_content(prompt)
    txt = safe_response_text(resp)
    # Se estourar tokens (finish_reason=2), tenta versão mais curta
    if txt.startswith("[Sem texto na resposta; finish_reason=2]"):
        short = prompt + "\n\nResponda de forma AINDA mais curta. Priorize listas em 1 linha."
        resp = model.generate_content(short)
        txt = safe_response_text(resp)
    return txt

def agente_marketing(topic, audience, offer, tone, budget, cpr,
                     model_name="gemini-2.5-flash",
                     gen_config=None):
    budget, cpr = validate_numbers(budget, cpr)
    prompt = build_prompt(topic, audience, offer, tone)

    if gen_config is None:
        gen_config = {"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 3072}  # um pouco mais longo

    model = genai.GenerativeModel(model_name=model_name, generation_config=gen_config)
    ideas_text = _try_generate(model, prompt)

    estimativa = budget / cpr
    return ideas_text, budget, cpr, estimativa

# ---------- Estilo “bot de marketing” ----------
st.set_page_config(page_title="Gemini MKT Express", page_icon="⚡", layout="centered")

# CSS leve para dar “cara de produto”
st.markdown("""
<style>
  .main { max-width: 900px; }
  .stTextInput>div>div>input::placeholder { color: #8b8b8b; opacity: 1; }
  .stTextInput>label, .stCaption, .st-emotion-cache-16idsys p { font-size: 0.95rem; }
  .pill { display:inline-block; padding:4px 10px; border-radius:999px; background:#222; color:#ddd; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("### ⚡ Gemini MKT Express — Ideias + CPR")
st.caption("Gere **3 ideias** + **2 legendas por ideia** e estime resultados (orçamento ÷ CPR).")

# API key via st.secrets (produção) ou os.environ (fallback local)
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_APIKEY_ETIC")
if not API_KEY:
    st.error("Defina a API Key em Secrets (GOOGLE_API_KEY) ou variável de ambiente.")
    st.stop()
genai.configure(api_key=API_KEY)

with st.form("form"):
    st.subheader("Configurações da campanha")

    # Exemplo visível, campos vazios
    with st.expander("Ver exemplo preenchido (apenas referência)"):
        st.markdown("""
**Tema/Nicho:** Almoço executivo (delivery para empresas)  
**Público:** Trabalhadores em horário de almoço na região central  
**Oferta/Ângulo:** Combo do dia + bebida por R$ 24,90 — entrega em 20 min  
**Tom de voz:** direto, amigável, foco em praticidade  
**Orçamento (R$):** 60 · **CPR (R$):** 3 · **Resultado:** cliques
        """)

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Tema/Nicho", value="", placeholder="Ex.: Pizzaria artesanal / Moda fitness / Clínica")
        audience = st.text_input("Público", value="", placeholder="Ex.: Jovens 18–30 na região central")
        offer = st.text_input("Oferta/Ângulo", value="", placeholder="Ex.: Quarta em dobro / Frete grátis")
    with col2:
        tone = st.text_input("Tom de voz", value="", placeholder="Ex.: direto e jovem · amigável · premium")
        budget = st.text_input("Orçamento (R$)", value="", placeholder="Ex.: 300")
        cpr = st.text_input("CPR — custo por resultado (R$)", value="", placeholder="Ex.: 2.5")
        resultado_nome = st.text_input("Resultado medido pelo CPR", value="", placeholder="Ex.: cliques, leads, vendas")

    st.caption(
        "Dicas: "
        "<span class='pill'>Oferta clara</span>"
        "<span class='pill'>CTA objetivo</span>"
        "<span class='pill'>Sem promessas de performance</span>",
        unsafe_allow_html=True
    )

    submitted = st.form_submit_button("Gerar ideias e estimativa")

# Validação de campos obrigatórios
if submitted:
    campos = [topic, audience, offer, tone, budget, cpr]
    if not all((c or "").strip() for c in campos):
        st.warning("Preencha todos os campos antes de gerar.")
        st.stop()

if submitted:
    try:
        resultado_nome = (resultado_nome or "resultados").strip()

        ideas_text, budget_v, cpr_v, estimativa = agente_marketing(
            topic, audience, offer, tone, budget, cpr,
            model_name="gemini-2.5-flash",
            gen_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 3072}
        )

        st.markdown("### ✅ Ideias & Legendas")
        if ideas_text.startswith("[Sem texto"):
            st.warning("Resposta ficou longa demais. Tente um **tom mais objetivo** e **legendas menores**.")
        else:
            st.write(ideas_text)

        st.markdown("### 📊 Estimativa (Python)")
        st.write(f"Resultados ≈ orçamento / CPR → {budget_v}/{cpr_v} = **{int(estimativa)} {resultado_nome}**")
        st.caption("Observação: estimativa é aproximação; não é garantia de performance.")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.exception(e)