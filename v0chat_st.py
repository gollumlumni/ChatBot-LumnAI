import os, pathlib, streamlit as st
from openai import OpenAI
from dotenv import load_dotenv   # só para rodar localmente
from pathlib import Path
from string import Template
import json
import re
import pandas as pd



link = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT06GPLcaSYiLGz3BgrIb8NLSmYlxXRQcKKXHxnlSXUjJM1poE5Z427CjJZv5iJMUnYVAvCZPuL0NnX/pub?output=csv'
colegio = pd.read_csv(link, skiprows= 1)
colegio.drop(columns= 'Unnamed: 0', inplace= True)

colegio.set_index('Variável', inplace= True)
colegio = colegio.to_dict()['Input']

# === CARREGAMENTO DOS PROMPTS ===
raw_qualificacao = Path("prompt_qualificacao.txt").read_text(encoding="utf8")
raw_agendamento = Path("prompt_agendamento.txt").read_text(encoding="utf8")
PROMPT_QUALIFICACAO = Template(raw_qualificacao).safe_substitute(**colegio)
PROMPT_AGENDAMENTO = Template(raw_agendamento).safe_substitute(**colegio)

# === CONFIG OPENAI ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* fonte + cores do tema */
html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align:center;'>Lumn<span style='color:#fc7d55;'>AI</span></h1>
<h3 style='text-align:center; margin-top:-6px;'>ChatBot Educacional</h3>
<p style='text-align:center;'>beta · Qualificação e Agendamento </p><hr>
""", unsafe_allow_html=True)

# === ESTADO INICIAL ===
if "messages" not in st.session_state:
    st.session_state.lead_qualificado = False
    st.session_state.messages = [
        {"role": "system", "content": PROMPT_QUALIFICACAO}
    ]

# === MOSTRA HISTÓRICO DE CONVERSA ===
for m in st.session_state.messages[1:]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# === INPUT DO USUÁRIO ===
if user := st.chat_input("Digite aqui…"):
    st.session_state.messages.append({"role": "user", "content": user})
    with st.chat_message("user"):
        st.markdown(user)

    # CHAMADA OPENAI
    prompt_usado = PROMPT_AGENDAMENTO if st.session_state.lead_qualificado else PROMPT_QUALIFICACAO
    st.session_state.messages[0] = {"role": "system", "content": prompt_usado}

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        max_tokens=400,
        temperature=0.7,
    )

    message = resp.choices[0].message
    answer = message.content.strip() if message.content else ""

    # === VERIFICA JSON DE FUNÇÃO ===
    code_block_match = re.search(r"```json\s*(\{.*?\})\s*```", answer, re.DOTALL)
    json_match = code_block_match.group(1) if code_block_match else None

    if json_match:
        args = json.loads(json_match)
        nome_funcao = args.get("name")

        # === FLUXO: REGISTRAR LEAD ===
        if nome_funcao == "registrar_lead":
            st.session_state.lead_qualificado = True
            print(f"Dados de qualificação:\n\n{args}")

            hist = st.session_state.messages[1:]
            st.session_state.messages = [{"role": "system", "content": PROMPT_AGENDAMENTO}] + hist

            # Gera a resposta automática do assistente para iniciar agendamento
            resposta_agendamento = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                max_tokens=200,
                temperature=0.7
            ).choices[0].message.content.strip()

            with st.chat_message("assistant"):
                st.markdown(resposta_agendamento)

            st.session_state.messages.append({
                "role": "assistant",
                "content": resposta_agendamento
            })

        # === FLUXO: AGENDAR VISITA ===
        elif nome_funcao == "agendar_visita":
            print(f"Dados de agendamento:\n\n{args}")

            mensagem = "Visita agendada com sucesso! 😊 Posso te ajudar com mais alguma coisa?"

            with st.chat_message("assistant"):
                st.markdown(mensagem)

            st.session_state.messages.append({
                "role": "assistant",
                "content": mensagem
            })
            

    else:
        # Sem JSON, apenas responde normalmente
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

