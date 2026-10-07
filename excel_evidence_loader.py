import os
import pandas as pd
import json
from pathlib import Path
from log_service import salvar_etapa

def carregar_evidencias_excel(caminho_excel: str) -> dict:
    """
    Lê uma planilha Excel contendo evidências já mapeadas e converte para a estrutura JSON
    esperada pela etapa de Quesitos (e salva no formato padrão do sistema).
    
    Colunas aceitas (com busca flexível):
    - Tipo de Evidência / tipo
    - Conteúdo / Trecho / conteudo
    - Resumo / resumo
    - Referência / referencia
    """
    if not os.path.exists(caminho_excel):
        raise FileNotFoundError(f"Arquivo de evidências não encontrado: {caminho_excel}")

    df = pd.read_excel(caminho_excel)

    # Identificação flexível das colunas
    col_tipo = None
    col_conteudo = None
    col_resumo = None
    col_referencia = None

    for col in df.columns:
        col_lower = str(col).lower()
        if "tipo" in col_lower and not col_tipo:
            col_tipo = col
        elif ("conte" in col_lower or "trecho" in col_lower) and not col_conteudo:
            col_conteudo = col
        elif "resumo" in col_lower and not col_resumo:
            col_resumo = col
        elif ("refer" in col_lower or "ref" in col_lower) and not col_referencia:
            col_referencia = col

    evidencias = []
    for _, row in df.iterrows():
        tipo = str(row[col_tipo]).strip() if col_tipo and pd.notna(row[col_tipo]) else "GERAL"
        conteudo = str(row[col_conteudo]).strip() if col_conteudo and pd.notna(row[col_conteudo]) else ""
        resumo = str(row[col_resumo]).strip() if col_resumo and pd.notna(row[col_resumo]) else ""
        referencia = str(row[col_referencia]).strip() if col_referencia and pd.notna(row[col_referencia]) else ""

        if conteudo or resumo:
            evidencias.append({
                "tipo": tipo,
                "conteudo": conteudo,
                "resumo": resumo,
                "referencia": referencia
            })

    # Formato estruturado padrão esperado pelo pipeline
    resultado_estruturado = {
        "resposta_estruturada": {
            "GERAL": evidencias
        }
    }

    return resultado_estruturado

def injetar_evidencias_em_execucao(caminho_excel: str, pasta_execucao: str, num_blocos: int = 1) -> list[str]:
    """
    Carrega evidências do Excel e salva como arquivos json de provas para a execução informada.
    Se num_blocos > 1, divide proporcionalmente ou disponibiliza o conjunto completo para cada bloco.
    """
    dados_evidencias = carregar_evidencias_excel(caminho_excel)
    evidencias_lista = dados_evidencias["resposta_estruturada"]["GERAL"]
    
    arquivos_gerados = []
    
    # Dividir entre os blocos se necessário ou fornecer lote completo
    if num_blocos <= 1:
        fat = [evidencias_lista]
    else:
        # Divisão proporcional das evidências entre os blocos
        tamanho_fatia = max(1, len(evidencias_lista) // num_blocos)
        fat = []
        for i in range(num_blocos):
            inicio = i * tamanho_fatia
            fim = (i + 1) * tamanho_fatia if i < num_blocos - 1 else len(evidencias_lista)
            fat.append(evidencias_lista[inicio:fim])

    for i in range(num_blocos):
        bloco_id = f"{i+1:02d}"
        evids_bloco = fat[i] if i < len(fat) else evidencias_lista
        payload = {
            "resposta_estruturada": {
                "GERAL": evids_bloco
            }
        }
        salvar_etapa(f"provas_bloco_{bloco_id}", f"Evidências importadas do Excel: {caminho_excel}", payload, pasta_execucao)
        caminho_json = os.path.join(pasta_execucao, f"provas_bloco_{bloco_id}_resposta.json")
        arquivos_gerados.append(caminho_json)

    return arquivos_gerados
