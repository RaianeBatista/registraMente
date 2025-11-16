
import streamlit as st
import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from agent_service import process_user_input

st.set_page_config(
    page_title="RegistraMente",
    page_icon="🧠",
    layout="wide",
)




st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        font-size: 16px; /* Tamanho de fonte base */
    }

    /* Estilo para fixar o cabeçalho (pode precisar de ajuste nas classes) */
    .css-1lcbmhc, .css-1qxtsq7, .css-fg4pbf { /* Essas classes são tentativas e podem mudar */
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #7B68EE; /* Cor de fundo do seu tema */
        padding: 10px 20px;
        color: #F5FFFA; /* Cor do texto do seu tema */
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Sutil sombra para destacar */
    }
    /* Adicionar preenchimento ao conteúdo principal para evitar sobreposição */
    .block-container {
        padding-top: 5rem; /* Ajustar conforme a altura do seu cabeçalho fixo */
    }

    /* Limitar a largura do chat input */
    div.st-chat-input-container { /* Isso pode precisar de ajuste, inspecione o elemento no navegador */
        max-width: 700px; /* Largura máxima desejada */
        margin-left: auto;
        margin-right: auto; /* Centralizar o input */
    }
    </style>
""", unsafe_allow_html=True)

st.title("RegistraMente") # O título principal do seu aplicativo

st.write("**Olá! Este é o seu assistente pessoal**.  \nDescreva um evento, tarefa ou rotina, e eu salvarei tudo para você.")

# Removi as credenciais Stackspot e a autenticação
# Your Stackspot Credentials
# CLIENT_ID = "7498f99d-0bdc-4d72-bd6f-bc608adf1ec1"
# CLIENT_KEY = "O13K5vk3RGnWpw8m72wDL1dkfJzcYKSIjHhG5jbL4f6dS0fV14g5tY3l2A50d0DV"
# REALM = "stackspot-freemium"

# AUTH_URL = f"https://idm.stackspot.com/{REALM}/oidc/oauth/token"
# AGENT_CHAT_URL = "https://genai-inference-app.stackspot.com/v1/agent/01KA3ZX17MKS47VQ6D54VVWAHY/chat"

# Authenticate once and store the JWT token
# if "jwt_token" not in st.session_state:
#     try:
#         print("Autenticando com Stackspot...")
#         st.session_state.jwt_token = authenticate(CLIENT_ID, CLIENT_KEY, AUTH_URL)
#         print("Autenticação bem-sucedida! JWT obtido.")
#     except requests.exceptions.RequestException as e:
#         st.error(f"Ocorreu um erro de autenticação: {e}")
#         print(f"Ocorreu um erro de autenticação: {e}")
#         if e.response is not None:
#             print(f"Conteúdo da resposta: {e.response.text}")
#             st.error(f"Conteúdo da resposta: {e.response.text}")

# Initialize Firebase Admin SDK (if not already initialized by main.py)
# Removi a inicialização aqui, pois agent_service.py já lida com isso.
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client() # Obtenha uma referência para o banco de dados Firestore


# Placeholder for future interactions
st.subheader("**O que você quer registrar hoje?** 📝")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Ex: Reunião de alinhamento amanhã às 14h no Google Meet"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    print(f"[Log] Usuário enviou: {user_prompt}")

    with st.chat_message("agent"):
        # Chamar a nova função de serviço do agente
        try:
            print(f"[Log] Chamando process_user_input com: {user_prompt}")
            agent_response, updated_memory = process_user_input(user_prompt)
            st.markdown(agent_response)
            st.session_state.messages.append({"role": "agent", "content": agent_response})
            st.session_state.current_memory = updated_memory # Armazenar a memória atualizada
            
            # Salvar a memória atualizada no Firestore
            doc_ref = db.collection("agent_memories").document("user_memory")
            doc_ref.set(st.session_state.current_memory)
            
            print(f"[Log] Resposta do agente: {agent_response}")
            print(f"[Log] Memória atualizada (para depuração): {updated_memory}")
            print(f"[Log Debug - app.py] st.session_state.current_memory antes do save: {st.session_state.current_memory}") # Novo log
        except Exception as e:
            st.error(f"Ocorreu um erro ao interagir com o agente local: {e}")
            print(f"[Log] Erro ao interagir com o agente local: {e}")

with st.sidebar:
    st.subheader("Minha Agenda 📅")

    # Inicializa st.session_state.current_memory se não existir
    if "current_memory" not in st.session_state:
        st.session_state.current_memory = {"events": []}

    # Lê e exibe as memórias do agente do Firestore ou usa a memória da sessão
    try:
        with st.spinner("Carregando eventos..."):
            doc_ref = db.collection("agent_memories").document("user_memory")
            doc = doc_ref.get()
            if doc.exists:
                memory = doc.to_dict()
                if "events" not in memory: memory["events"] = []
            else:
                memory = {"events": []}
            
            # Se a memória da sessão estiver vazia ou não tiver eventos, use a do Firestore
            if not st.session_state.current_memory.get("events"):
                st.session_state.current_memory = memory
            else:
                # Caso contrário, se a sessão tiver eventos, use a sessão (já foi atualizada pelo chat)
                memory = st.session_state.current_memory

        print(f"[Log Debug - app.py] Memória carregada na sidebar: {memory}") # Novo log
        st.write("**Eventos:**")
        if memory["events"]:
            for i, event_data in enumerate(memory["events"]):
                st.write(f"- **Título:** {event_data.get('title', 'N/A')}")
                st.write(f"  **Data:** {event_data.get('date', 'N/A')}")
                st.write(f"  **Hora:** {event_data.get('time', 'N/A')}")
                st.write(f"  **Assunto:** {event_data.get('description', 'N/A')}")
                st.write(f"  **Local:** {event_data.get('location', 'N/A')}")
                if st.button("Concluir", key=f"complete_event_{event_data.get('id')}"):
                    # Lógica para remover o evento
                    print(f"Removendo evento: {event_data.get('title')}")
                    # Encontrar o índice do evento pelo ID
                    event_id_to_remove = event_data.get('id')
                    st.session_state.current_memory["events"] = [event for event in st.session_state.current_memory["events"] if event.get('id') != event_id_to_remove]
                    # Atualizar Firestore
                    doc_ref = db.collection("agent_memories").document("user_memory")
                    doc_ref.set(st.session_state.current_memory)
                    st.rerun()
        else:
            st.write("Nenhum evento registrado ainda.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar as memórias do Firestore: {e}")
