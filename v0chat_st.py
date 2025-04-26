import os, pathlib, streamlit as st
from openai import OpenAI
from dotenv import load_dotenv          # só útil localmente

load_dotenv()                           # lê .env se existir
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR      = pathlib.Path(__file__).parent
SYSTEM_PROMPT = (BASE_DIR / "prompt_escola.txt").read_text(encoding="utf8")


# ───────────────────────────────
# 2) Estado de conversa
# ──────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# mostra histórico
for m in st.session_state.messages[1:]:            # pula o system
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ──────────────────────────────────
# 3) Entrada do usuário
# ──────────────────────────────────
if user := st.chat_input("Digite aqui…"):
    st.session_state.messages.append({"role": "user", "content": user})
    with st.chat_message("user"):
        st.markdown(user)

    # chamada à API
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        max_tokens=400,
        temperature=0.4,
    )
    answer = resp.choices[0].message.content.strip()

    # mostra resposta
    with st.chat_message("assistant"):
        st.markdown(answer)

    # salva no histórico
    st.session_state.messages.append({"role": "assistant", "content": answer})






