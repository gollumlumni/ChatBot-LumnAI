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


# inputando o template de prompt
raw = Path("prompt_template.txt").read_text(encoding="utf8")
t = Template(raw)
# 3) substitua só os $placeholders
system_prompt = t.safe_substitute(**colegio)

load_dotenv()                    # lê .env quando existe
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR      = pathlib.Path(__file__).parent
SYSTEM_PROMPT = system_prompt


print(system_prompt)
st.markdown(
    """
    <style>
    /* 1) Carrega a fonte */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* 2) Aplica a Outfit em todo o conteúdo Streamlit */
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
json
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


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# mostra histórico
for m in st.session_state.messages[1:]:            # pula o system
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


if user := st.chat_input("Digite aqui…"):
    st.session_state.messages.append({"role": "user", "content": user})
    with st.chat_message("user"):
        st.markdown(user)

    # chamada à API
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,          
        max_tokens=400,
        temperature=0.5,
    )

    message = resp.choices[0].message
    print(message)
    answer = message.content.strip() if message.content else ""

    # Verifica se há um JSON na resposta
    code_block_match = re.search(r"```json\s*(\{.*?\})\s*```", answer, re.DOTALL)

    if code_block_match:
        json_match = code_block_match.group(1)
    else:
        # Fallback: procura qualquer JSON "solto"
        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
        json_match = json_match.group(0) if json_match else None

    if json_match:
        print('chamou a função')
        args = json.loads(json_match)

        print("Dados recebidos:", args)

        mensagens_contexto = st.session_state.messages[-6:]

            # Formata contexto com mensagens anteriores + dados do colégio
        contexto_para_resposta = [
                {"role": "system", "content": f"""Você é um atendente simpático do {colegio['nome_da_escola']}.
                Como informações complementares sobre o colégio: \n{colegio}"""}
            
            ] + mensagens_contexto + [{
                    "role": "user",
                    "content": "Você acabou de registrar informações do responsável ou agendou uma visita. Envie uma mensagem bem curta cordial continuando a conversa e confirmando o registro. Se for registro de Lead, perguntar se a pessoa não quer fazer uma visita ao colégio. Se for um agendamento, pergunte se pode ajudar com mais alguma coisa(não recomende outro agendamento)."
                }]

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=contexto_para_resposta,
            max_tokens=100,
            temperature=0.2
        ).choices[0].message.content.strip()

        with st.chat_message("assistant"):
            st.markdown(resposta)

        st.session_state.messages.append({"role": "assistant", "content": resposta})

    elif answer:
        # se não houve chamada de função, é porque ainda faltam dados
        print(f'Ainda estou aqui:\n{user}\n')
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role":"assistant","content":answer})








