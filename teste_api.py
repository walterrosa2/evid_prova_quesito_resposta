import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERRO: GOOGLE_API_KEY não encontrada no .env!")
    exit(1)

genai.configure(api_key=api_key)

import os
from dotenv import load_dotenv
import google.generativeai as genai
import sys

# Força a exibição UTF-8 no stdout (evita problema com caracteres no console)
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERRO: GOOGLE_API_KEY nao encontrada no .env!")
    exit(1)

genai.configure(api_key=api_key)

print("[INFO] Buscando modelos disponiveis na API...")
try:
    modelos = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelos.append(m.name)
            print(f"- {m.name}")
    
    # Tenta usar o primeiro modelo "flash" encontrado, senao pega o primeiro da lista
    modelo_escolhido = next((m for m in modelos if "flash" in m), modelos[0] if modelos else "gemini-1.5-flash")
    
    print(f"\n[INFO] Instanciando o modelo LLM: {modelo_escolhido}...")
    modelo = genai.GenerativeModel(modelo_escolhido.replace("models/", ""))
    
    resp = modelo.generate_content("Diga 'Conexão bem sucedida com o LLM!'")
    print("\n[SUCESSO] Resposta do motor LLM:")
    print(resp.text)
except Exception as e:
    print(f"\n[FALHA] Erro de comunicacao com o Gemini: {e}")
