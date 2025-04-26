import os, pathlib, streamlit as st
from openai import OpenAI
from dotenv import load_dotenv   # só para rodar localmente

load_dotenv()                    # lê .env quando existe
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR      = pathlib.Path(__file__).parent
SYSTEM_PROMPT = (BASE_DIR / "prompt_escola.txt").read_text(encoding="utf8")


st.markdown(
    """
    <style>
    /* 1) Carrega a fonte */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* 2) Aplica a Outfit em todo o conteúdo Streamlit */
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }

    /* 3) Ajusta títulos explicitamente (opcional) */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;          /* deixa títulos em bold */
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <h1 style='text-align:center; margin-top:0'>
        <span style='color:#ff5c35;'>Lumn</span><b>AI</b> ChatBot
    </h1>
    <p style='text-align:center; font-size:0.9rem; color:gray;'>
        LumnAI ChatBot · beta
    </p>
    <hr style='margin-top:1rem;'>
    """,
    unsafe_allow_html=True
)

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






