# config.py
from pathlib import Path

import os

# === CHAVE DA API GEMINI ===
GOOGLE_API_KEY = "AIzaSyAmKniS7s6odyTWF1Pm9sV7FJtQbG3xFnc"  # Substitua pela chave real



# Raiz onde ficam as execuções
EXECUCOES_ROOT = Path(r"C:\Users\walte\OneDrive\Workspace\IA\Cruvinel\Projeto Evidencias e Provas\P4\execucoes")

def get_exec_path(nome_execucao: str) -> Path:
    """Retorna a pasta completa da execução."""
    return (EXECUCOES_ROOT / nome_execucao).resolve()

