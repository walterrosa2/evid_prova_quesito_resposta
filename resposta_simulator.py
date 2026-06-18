
from prompt_engine import run_prompt
import json

def simular_respostas(quesitos: dict, evidencias: dict, contexto_opcional: str = "") -> dict:
    etapa = "ETAPA 4 – RESPOSTA QUESITOS"
    funcao = (
        "Responda tecnicamente aos quesitos com base nas evidências fornecidas. "
        "Cada resposta deve conter os campos: resposta (string), status_tecnico (string), "
        "justificativa_tecnica (string) e observacoes_adicionais (string). "
        "Agrupe por chave (índice) ou use 'GERAL' quando não houver índices."
    )

    texto_entrada = (
        "Quesitos a serem respondidos (JSON):\n"
        f"{json.dumps(quesitos, ensure_ascii=False, indent=2)}\n\n"
        "Evidências disponíveis (JSON):\n"
        f"{json.dumps(evidencias, ensure_ascii=False, indent=2)}\n"
    )
    if contexto_opcional:
        texto_entrada += f"\nContexto adicional (bloco do processo):\n{contexto_opcional}\n"

    resultado = run_prompt(etapa, funcao, texto_entrada, prompt_name="prompt_etapa_respostas")

    if not isinstance(resultado, dict):
        return {"erro": "Falha na chamada ao modelo"}

    if "resposta_estruturada" in resultado and isinstance(resultado["resposta_estruturada"], dict):
        return resultado["resposta_estruturada"]

    if "resposta_bruta" in resultado:
        return {"erro": "Resposta fora do padrão", "resposta_bruta": resultado.get("resposta_bruta")}

    return {"erro": "Nenhuma resposta estruturada recebida"}
