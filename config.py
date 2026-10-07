# config.py
from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv(override=True)

# === CHAVE DA API GEMINI ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")



# Raiz onde ficam as execuções
EXECUCOES_ROOT = Path(r"C:\Users\walte\OneDrive\Workspace\IA\Cruvinel\Projeto Evidencias e Provas\P4\execucoes")

def get_exec_path(nome_execucao: str) -> Path:
    """Retorna a pasta completa da execução."""
    return (EXECUCOES_ROOT / nome_execucao).resolve()

