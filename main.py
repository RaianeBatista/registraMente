from dotenv import load_dotenv
from dotenv import find_dotenv
import os
from agent_service import process_user_input # Importa a nova função

load_dotenv(find_dotenv())

# Exemplo de como usar o agent_service
if __name__ == "__main__":
    print("Agent Service iniciado. Use a interface Streamlit para interagir.")
    # Exemplo de interação direta (apenas para demonstração)
    # response, memory = process_user_input("Lembre-me de comprar pão amanhã de manhã.")
    # print(f"Resposta: {response}")
    # print(f"Memória atualizada: {memory}")