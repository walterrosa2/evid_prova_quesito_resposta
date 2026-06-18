
from prompt_engine import run_prompt
from log_console import log
import json

def mapear_provas(texto_bloco: str, indices: dict | None = None) -> dict:
    etapa = "ETAPA 2 – PROVAS & EVIDÊNCIAS"
    funcao = (
        "Mapeie provas e evidências do trecho fornecido. "
        "Se índices temáticos forem informados, organize por índice; "
        "caso contrário, organize tudo sob a chave 'GERAL'. "
        "Cada evidência deve conter: tipo, conteudo, resumo, referencia."
    )

    # Montagem da entrada
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
        partes.append("")  # linha em branco

    partes.append("Texto do processo:")
    partes.append(texto_bloco)
    texto_entrada = "\n".join(partes)

    # Execução com prompt dedicado da etapa
    resultado = run_prompt(etapa, funcao, texto_entrada, prompt_name="prompt_etapa_evidencias")

    if not isinstance(resultado, dict):
        return {"erro": "Falha na chamada ao modelo"}

    # Preferência por resposta estruturada
    if "resposta_estruturada" in resultado and isinstance(resultado["resposta_estruturada"], (dict, list)):
        dados = resultado["resposta_estruturada"]

        # Normalização:
        # 1) Se vier lista de evidências, envelopa em {'GERAL': [...]}
        if isinstance(dados, list):
            evids = []
            for item in dados:
                if isinstance(item, dict):
                    tipo = item.get("tipo")
                    cont = item.get("conteudo")
                    resu = item.get("resumo")
                    ref  = item.get("referencia")
                    if all([tipo, cont, resu, ref]):
                        evids.append({"tipo": tipo, "conteudo": cont, "resumo": resu, "referencia": ref})
            return {"GERAL": evids}

        # 2) Se vier dict por grupos/índices, validar cada evidência
        saida: dict[str, list] = {}
        for chave, itens in (dados or {}).items():
            provas_validas = []
            if isinstance(itens, list):
                for item in itens:
                    if not isinstance(item, dict):
                        continue
                    tipo = item.get("tipo")
                    cont = item.get("conteudo")
                    resu = item.get("resumo")
                    ref  = item.get("referencia")
                    if all([tipo, cont, resu, ref]):
                        provas_validas.append({"tipo": tipo, "conteudo": cont, "resumo": resu, "referencia": ref})
                    else:
                        log(f"⚠️ Prova incompleta ignorada em {chave}: {item}", tipo="alerta")
            if provas_validas:
                saida[chave] = provas_validas

        if not saida and not indices:
            # Se nada válido e sem índices, retorne contêiner vazio GERAL
            return {"GERAL": []}
        return saida

    # Retorno bruto em caso de erro de formatação
    if "resposta_bruta" in resultado:
        log("⚠️ A IA retornou resposta fora do padrão estruturado.", tipo="alerta")
        return {"erro": "Retorno não estruturado. Tente reexecutar o bloco.", "resposta_bruta": resultado.get("resposta_bruta")}

    return {"erro": "Nenhuma evidência retornada"}
