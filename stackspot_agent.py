
import requests
import json
import speech_recognition as sr

# Your Stackspot Credentials
CLIENT_ID = "7498f99d-0bdc-4d72-bd6f-bc608adf1ec1"
CLIENT_KEY = "O13K5vk3RGnWpw8m72wDL1dkfJzcYKSIjHhG5jbL4f6dS0fV14g5tY3l2A50d0DV"
REALM = "stackspot-freemium"

AUTH_URL = f"https://idm.stackspot.com/{REALM}/oidc/oauth/token"
AGENT_CHAT_URL = "https://genai-inference-app.stackspot.com/v1/agent/01KA3ZX17MKS47VQ6D54VVWAHY/chat"

def authenticate(client_id, client_key, auth_url):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_key
    }
    response = requests.post(auth_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def chat_with_agent(jwt_token, agent_chat_url, user_prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {
        "streaming": False, # Alterado para False para desativar o streaming
        "user_prompt": user_prompt,
        "stackspot_knowledge": False,
        "return_ks_in_response": True
    }
    response = requests.post(agent_chat_url, headers=headers, json=payload)
    response.raise_for_status()
    
    # Processa a resposta completa, já que o streaming está desativado
    response_json = response.json()
    print(f"[Log - chat_with_agent] Resposta JSON completa do agente: {response_json}") # Adicionei este log
    agent_message = ""
    if "message" in response_json:
        agent_message = response_json["message"]
        print(agent_message, end='', flush=True)
    print() # New line after the full response
    return agent_message

def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Pressione ENTER para começar a falar...")
        input()
        print("Ouvindo... Fale agora!")
        try:
            audio = r.listen(source, phrase_time_limit=10) # Limite de tempo para a frase
            print("Processando áudio...")
            text = r.recognize_google(audio, language="pt-BR")
            
            if "sair" in text.lower() or "parar" in text.lower() or "finalizar" in text.lower():
                return "sair"

            print(f"Você disse: {text}")
            return text
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return None # Retorna None para indicar que nada foi reconhecido
        except sr.RequestError as e:
            print(f"Não foi possível solicitar resultados do serviço de reconhecimento de fala; {e}")
            return ""

if __name__ == "__main__":
    try:
        print("Autenticando com Stackspot...")
        jwt = authenticate(CLIENT_ID, CLIENT_KEY, AUTH_URL)
        print("Autenticação bem-sucedida! JWT obtido.")
        
        print("\nOlá! Como posso ajudar você hoje? Se quiser registrar algum evento ou acontecimento do seu dia, é só me contar!")
        
        print("\nInicie seu chat com o agente. Pressione ENTER para falar, ou diga 'sair' para encerrar.")
        while True:
            user_input = get_voice_input()
            if user_input is None: # User pressed Enter without speaking, or no speech was recognized
                continue
            if user_input == "sair":
                print("Encerrando o chat.")
                break
            
            if user_input:
                print("Agente: ", end='')
                chat_with_agent(jwt, AGENT_CHAT_URL, user_input)
            
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro: {e}")
        if e.response is not None:
            print(f"Conteúdo da resposta: {e.response.text}")
