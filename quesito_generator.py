
from prompt_engine import run_prompt
from log_console import log
import json

def gerar_quesitos(texto_bloco: str, indices: dict | None = None, evidencias: dict | None = None) -> dict:
    etapa = "ETAPA 3 – QUESITOS AUTORA"
    funcao = (
        "Elabore quesitos técnicos a partir do texto do processo e das evidências disponíveis. "
        "Se índices forem informados, agrupe por índice; caso contrário, use a chave 'GERAL'. "
        "Retorne APENAS JSON, sendo cada grupo uma lista de strings (quesitos)."
    )

    partes = []
    if indices:
        partes.append("[ÍNDICES TEMÁTICOS DO BLOCO]")
        for cod, item in indices.items():
            if isinstance(item, dict):
                titulo = item.get("titulo", "")
                resumo = item.get("resumo", "")
                referencia = item.get("referencia", "")
                partes.append(f"{cod} - {titulo} (Resumo: {resumo}. Ref: {referencia})")
            else:
                partes.append(f"{cod} - {item}")
        partes.append("")

    if evidencias:
        partes.append("[EVIDÊNCIAS DISPONÍVEIS - JSON]")
        partes.append(json.dumps(evidencias, ensure_ascii=False, indent=2))
        partes.append("")

    partes.append("Texto do processo:")
    partes.append(texto_bloco)
    texto_entrada = "\n".join(partes)

    resultado = run_prompt(etapa, funcao, texto_entrada, prompt_name="prompt_etapa_quesitos")

    if not isinstance(resultado, dict):
        return {"erro": "Falha na chamada ao modelo"}

    if "resposta_estruturada" in resultado and isinstance(resultado["resposta_estruturada"], (dict, list)):
        dados = resultado["resposta_estruturada"]
        # Se vier lista simples, envelopar
        if isinstance(dados, list):
            # manter apenas strings
            qs = [q for q in dados if isinstance(q, str) and q.strip()]
            return {"GERAL": qs}
        # Se vier dict:
        saida = {}
        for chave, lista in (dados or {}).items():
            if isinstance(lista, list):
                qs = [q for q in lista if isinstance(q, str) and q.strip()]
                if qs:
                    saida[chave] = qs
        if not saida and not indices:
            return {"GERAL": []}
        return saida

    if "resposta_bruta" in resultado:
        return {
            "erro": "Resposta fora do padrão",
            "resposta_bruta": resultado.get("resposta_bruta")
        }

    return {"erro": "Nenhum quesito retornado"}
