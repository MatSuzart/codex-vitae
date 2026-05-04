"""
app.py – Interface Streamlit do Life Balance AI
Como rodar: streamlit run src/app.py
Documentação Streamlit: https://docs.streamlit.io/get-started/tutorials/create-an-app
"""
import streamlit as st
from src.orchestrator import run

# ── Configuração da página ───────────────────────────────────
st.set_page_config(
    page_title="Life Balance AI",
    page_icon="⚖️",
    layout="centered",
)

# ── Título e descrição ───────────────────────────────────────
st.title("⚖️ Life Balance AI")
st.caption("Seu assistente pessoal de equilíbrio — Agenda · Finanças · Notícias")

st.divider()

# ── Atalhos rápidos ──────────────────────────────────────────
st.subheader("⚡ Atalhos rápidos")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 Status do dia", use_container_width=True):
        st.session_state["question"] = "Como está meu dia hoje? Me dê um resumo completo."

with col2:
    if st.button("💰 Saúde financeira", use_container_width=True):
        st.session_state["question"] = "Como estão minhas finanças este mês?"

with col3:
    if st.button("📰 Briefing de notícias", use_container_width=True):
        st.session_state["question"] = "Me dê o briefing de notícias de hoje"

st.divider()

# ── Campo de pergunta ────────────────────────────────────────
question = st.text_input(
    "💬 Faça uma pergunta:",
    value=st.session_state.get("question", ""),
    placeholder="Ex: Como está minha semana? / Estou dentro do orçamento?",
)

if st.button("Perguntar", type="primary") and question:
    with st.spinner("Consultando seus agentes..."):
        try:
            resposta = run(question)
            st.success("✅ Resposta pronta!")
            st.markdown(resposta)
        except Exception as e:
            st.error(f"Erro: {e}")
            st.info("Verifique se o arquivo .env está configurado corretamente.")

    # Limpa o atalho após usar
    if "question" in st.session_state:
        del st.session_state["question"]

# ── Rodapé com instruções ────────────────────────────────────
with st.expander("ℹ️ Como configurar"):
    st.markdown("""
    **Pré-requisitos:**
    1. Copie `.env.example` para `.env` e preencha as credenciais
    2. Instale dependências: `pip install -r requirements.txt`
    3. Crie `data/extrato.csv` com seus dados financeiros
    4. Configure as credenciais do Trello (veja `.env.example`)

    **Credenciais necessárias:**
    - **Gemini (gratuito):** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    - **Trello:** [trello.com/app-key](https://trello.com/app-key)
    - **NewsAPI (gratuito):** [newsapi.org/register](https://newsapi.org/register)
    """)
