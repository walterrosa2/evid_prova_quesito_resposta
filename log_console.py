# evid_app/log_console.py

from datetime import datetime

# Códigos ANSI para cores
CORES = {
    "info": "\033[94m",      # azul
    "sucesso": "\033[92m",   # verde
    "erro": "\033[91m",      # vermelho
    "alerta": "\033[93m",    # amarelo
    "neutro": "\033[0m",     # reset (padrão)
}

def log(mensagem: str, icone: str = "ℹ️", tipo: str = "info"):
    """
    Exibe mensagem formatada no terminal com ícone, timestamp e cor.
    
    Parâmetros:
    - mensagem: texto a ser exibido
    - icone: emoji ou símbolo de destaque
    - tipo: 'info', 'sucesso', 'erro', 'alerta'
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    cor = CORES.get(tipo, CORES["neutro"])
    reset = CORES["neutro"]
    print(f"{cor}[{icone}] {timestamp} - {mensagem}{reset}")
