import os, pathlib, streamlit as st
from openai import OpenAI
from dotenv import load_dotenv   # só para rodar localmente
from pathlib import Path
from string import Template
import json
import re



colegio = {
    "nome_atendente":       "Victória",
    "nome_da_escola":       "Colégio Horizonte",
    "tom_de_voz":           "Cordial e Profissional",
    "personalizacao_tom":   "Você deve, sempre que possível, usar emojis, responder de maneira alegre",
    "segmentos":            "Infantil I-Jardim II; Fund. I-II; Médio",
    "links_publi":          "link de video 1, link do site",
    "periodos":             "Matutino (07h30-12h), Vespertino (13h30-18h)",
    "contatos":             "Secretaria: secretaria@horizonte.com | (85) 3333-2222  ; Financeiro: financeiro@horizonte.com | (85) 3333-2222 ; Coordenação Pedagógica: coorpedag@horizonte.com | (85) 3333-2222",
    "endereco":             "Av. das Flores, 1234 - Fortaleza/CE",
    "matriculas":           "02/05/2025 a 31/07/2025 (taxa R$ 500)",
    "mensalidades":         "Infantil: R$1150; Fund I: R$1250; Fund II: R$1350; Médio: R$1550",
    "info_geral_escola":    "O Colégio Horizonte conta com uma infraestrutura moderna e acolhedora, com salas de aula amplas e iluminadas, laboratórios de Ciências e Informática equipados com recursos de última geração e espaços de convivência para promover a interação entre os alunos. Nossa metodologia baseia-se no aprendizado ativo, com projetos interdisciplinares, uso de tecnologias educacionais e avaliações formativas que acompanham o desenvolvimento individual. Valorizamos o protagonismo dos estudantes, estimulando a criatividade e o pensamento crítico por meio de atividades práticas, oficinas temáticas e aulas ao ar livre. Além disso, oferecemos programas de reforço e apoio psicopedagógico, garantindo um ambiente seguro e colaborativo onde cada família e cada aluno se sentem parte de uma comunidade comprometida com a excelência acadêmica e o respeito mútuo. link de video 1, link de video 2.",
    "info_matricula":       "certidão de nascimento, CPF, comprovante de residência, RG dos responsáveis",
    "qualificacao":         "`nome_completo_responsavel`, `nome_completo_aluno`, `serie_aluno`, `email_responsavel`",
    "redirecionamentos":    "Se a dúvida for sobre boletos, pagamentos ou inadimplência, redirecione para o setor Financeiro. Para assuntos pedagógicos, como metodologia ou reclamações acadêmicas, oriente o contato com a Coordenação Pedagógica. Em casos gerais ou quando não souber a resposta, encaminhe para a Secretaria. Os contatos são: {contatos}.",
    "como_funciona_visita": "primeiro preenchemos cadastro e depois sugerimos datas",
    "few_shot":             """
                            Usuário: “Oi”  
                            Assistente: “Boa tarde! Tudo bem com você? O Colégio Horizonte fica feliz com o seu contato🥰. Meu nome é Victória. Para que eu possa seguir com o atendimento, pode me falar o seu nome e como posso te ajudar?”

                            Usuário: “Quanto custa a mensalidade do 7º ano?”  
                            Assistente: “Olá! Para o 7º ano (Fundamental II), a mensalidade de 2025 é de **R$ 1.350,00**. Gostaria de saber sobre descontos ou bolsas?”

                            Usuário: “Quero matricular minha filha no Jardim II.”  
                            Assistente: “Perfeito! Para iniciar a matrícula no Jardim II você precisará de:  
                            (1) certidão de nascimento  
                            (2) CPF da criança  
                            (3) comprovante de residência  
                            (4) RG dos responsáveis  
                            Deseja agendar uma visita ou receber o formulário digital?
                            
                            Usuário: (completou qualificação)
                            Assistente: “Mas, antes de qualquer coisa, gostaria de te convidar para vir até a escola e tomar um café com as nossas fundadoras e coordenadora pedagógica, o que você acha? 🥰 
                            Seria bom porque poderíamos aprofundar no nosso projeto pedagógico, contato com professores e rotina mesmo, além de você conhecer de pertinho esse espaço (que é incrível e, por mais que veja no vídeo, é muuuito diferente ver de perto🤞).”
                            """
}


# === CARREGAMENTO DOS PROMPTS ===
raw_qualificacao = Path("prompt_qualificacao.txt").read_text(encoding="utf8")
raw_agendamento = Path("prompt_agendamento.txt").read_text(encoding="utf8")
PROMPT_QUALIFICACAO = Template(raw_qualificacao).safe_substitute(**colegio)
PROMPT_AGENDAMENTO = Template(raw_agendamento).safe_substitute(**colegio)

# === CONFIG OPENAI ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === INTERFACE STREAMLIT (CSS E CABEÇALHO) ===
st.markdown("""<style>...</style>""", unsafe_allow_html=True)
st.markdown("""
<h1 style='text-align:center;'>Lumn<span style='color:#ff5c35;'>AI</span> ChatBot</h1>
<p style='text-align:center;'>LumnAI ChatBot · beta</p><hr>
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
            

    else:
        # Sem JSON, apenas responde normalmente
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})




