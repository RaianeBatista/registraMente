import json
import os
from datetime import datetime, date # Importar date também
import firebase_admin
from firebase_admin import credentials, firestore
import re # Importar o módulo re para expressões regulares
import dateparser # Importar dateparser

# Importar as ferramentas e utilitários que main.py usava
from utils.basemodel2tool import base_model2tool
from tools.daily_events import DailyEvents, Event
from stackspot_agent import authenticate, chat_with_agent, CLIENT_ID, CLIENT_KEY, REALM, AUTH_URL, AGENT_CHAT_URL
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Initialize Firebase Admin SDK (para garantir que esteja inicializado)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client() # Obtenha uma referência para o banco de dados Firestore

# Remove OpenAI client initialization
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_user_input(user_prompt: str):
    doc_ref = db.collection("agent_memories").document("user_memory")
    doc = doc_ref.get()
    if doc.exists:
        memory = doc.to_dict()
        if "events" not in memory: memory["events"] = []
    else:
        memory = {"events": []} # Não inicializar interações
        doc_ref.set(memory)

    actual_date = datetime.now().strftime("%d/%m/%Y")

    # Prepend actual_date to user_prompt for better context
    contextual_user_prompt = f"Hoje é {actual_date}. {user_prompt}"

    # Authenticate and chat with Stackspot agent
    jwt = authenticate(CLIENT_ID, CLIENT_KEY, AUTH_URL)
    agent_full_response = chat_with_agent(jwt, AGENT_CHAT_URL, contextual_user_prompt)

    print(f"[Log - chat_with_agent] Resposta JSON completa do agente: {agent_full_response}")

    if isinstance(agent_full_response, dict) and 'message' in agent_full_response:
        agent_response = agent_full_response['message']
    else:
        agent_response = agent_full_response # Se já for uma string, use-a diretamente

    if agent_response:
        print(f"[Log Debug] Conteúdo de agent_response: {agent_response}") # Log para depuração
        event_extracted = False
        
        # Exemplo de formato na resposta:
        # "Evento: Reunião Aleatória Data: 17/11/2025 Horário: 10:00 Assunto: Reunião Aleatória Local: https://meet.google.com/xyz-abc-def"
        event_pattern = re.compile(
            r"Evento: (.+?) "
            r"Data: (.+?) "
            r"Horário: (.+?) "
            r"Assunto: (.+?) "
            r"Local: (.+)"
        )
        
        match = event_pattern.search(agent_response)

        if match:
            try:
                title = match.group(1).strip()
                extracted_date_str = match.group(2).strip()
                time = match.group(3).strip()
                description = match.group(4).strip()
                location = match.group(5).strip()

                # Lógica de pós-processamento para correção da data
                corrected_date = extracted_date_str
                try:
                    # Tentar parsear a data extraída para validação
                    parsed_extracted_date = dateparser.parse(extracted_date_str, settings={'PREFER_DATES_FROM': 'future', 'RELATIVE_BASE': datetime.now()})

                    # Tentar parsear o user_prompt para inferir a data
                    parsed_user_prompt_date = dateparser.parse(user_prompt, settings={'PREFER_DATES_FROM': 'future', 'RELATIVE_BASE': datetime.now()})

                    # Se a data extraída for muito antiga e o user_prompt puder ser interpretado como futuro/relativo
                    # E se parsed_user_prompt_date não for nulo e for mais recente que parsed_extracted_date
                    if parsed_extracted_date and parsed_user_prompt_date and parsed_user_prompt_date.date() > date.today() and parsed_user_prompt_date.date() > parsed_extracted_date.date():
                        corrected_date = parsed_user_prompt_date.strftime("%d/%m/%Y")
                    elif parsed_extracted_date and parsed_extracted_date.date() < date.today() and parsed_user_prompt_date and parsed_user_prompt_date.date() >= date.today():
                        # Se a data extraída for no passado, mas o prompt sugere algo atual ou futuro
                        corrected_date = parsed_user_prompt_date.strftime("%d/%m/%Y")
                    elif not parsed_extracted_date and parsed_user_prompt_date:
                        # Se a data extraída não pôde ser parseada, mas o prompt sim
                        corrected_date = parsed_user_prompt_date.strftime("%d/%m/%Y")
                    elif parsed_extracted_date: # A data extraída é válida e razoável
                        corrected_date = parsed_extracted_date.strftime("%d/%m/%Y")
                    else:
                        # Último recurso: usar a data atual se nada mais funcionar
                        corrected_date = datetime.now().strftime("%d/%m/%Y")

                except Exception as date_e:
                    print(f"[Log] Erro ao corrigir data: {date_e}")
                    # Em caso de erro, manter a data original extraída
                    corrected_date = extracted_date_str

                new_event = Event(title=title, date=corrected_date, time=time, description=description, location=location)
                print(f"[Log Debug] Objeto Evento extraído: {new_event.dict()}") # Adicionar este print
                memory['events'].append(new_event.dict()) # Adiciona o evento formatado à lista de eventos
                event_extracted = True
                print(f"[Log] Evento extraído e adicionado: {new_event.dict()}")
            except Exception as e:
                print(f"[Log] Erro ao processar evento da resposta do agente: {e}")
        else:
            # Tentar regex sem Local, se o primeiro falhar
            event_pattern_no_location = re.compile(
                r"Evento: (.+?) "
                r"Data: (.+?) "
                r"Horário: (.+?) "
                r"Assunto: (.+)"
            )
            match = event_pattern_no_location.search(agent_response)
            if match:
                try:
                    title = match.group(1).strip()
                    date = match.group(2).strip()
                    time = match.group(3).strip()
                    description = match.group(4).strip()
                    location = ""
                    
                    new_event = Event(title=title, date=date, time=time, description=description, location=location)
                    print(f"[Log Debug] Objeto Evento extraído (sem Local): {new_event.dict()}")
                    memory['events'].append(new_event.dict())
                    event_extracted = True
                    print(f"[Log] Evento extraído e adicionado (sem Local): {new_event.dict()}")
                except Exception as e:
                    print(f"[Log] Erro ao processar evento sem Local da resposta do agente: {e}")
                
        # Não adicionar interações à memória, apenas eventos
        # if not event_extracted:
        #     memory['interactions'].append(f"Human: {user_prompt}")
        #     memory['interactions'].append(f"Assistant: {agent_response}")
        
        print(agent_response)
        print(f"[Log Debug] Memória antes de salvar - Eventos: {memory['events']}")
        # print(f"[Log Debug] Memória antes de salvar - Interações: {memory['interactions']}")

    doc_ref.set(memory) # Save memory to Firestore

    return agent_response, memory
