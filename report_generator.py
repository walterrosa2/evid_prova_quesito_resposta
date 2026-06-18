# report_generator.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

COLUNAS = [
    "Indice",
    "Categoria",               # Prova | Quesito | Resposta
    "TipoProva",               # só p/ Prova
    "Resumo",                  # só p/ Prova
    "Referencia",              # só p/ Prova
    "Quesito",                 # Quesito (texto) ou Quesito da Resposta
    "RespostaTecnica",         # só p/ Resposta
    "StatusTecnico",           # só p/ Resposta
    "JustificativaTecnica",    # só p/ Resposta
    "Observacoes",             # só p/ Resposta
    "Conteudo"                 # JSON do item bruto (quando fizer sentido)
]

def _to_df(linhas: List[Dict[str, Any]]) -> pd.DataFrame:
    if not linhas:
        return pd.DataFrame(columns=COLUNAS)
    # Garante todas as colunas
    for ln in linhas:
        for c in COLUNAS:
            ln.setdefault(c, "")
    return pd.DataFrame(linhas, columns=COLUNAS)

def exportar_excel(caminho_saida: Path, linhas: List[Dict[str, Any]]) -> Path:
    """
    Gera APENAS Excel com a consolidação de Provas, Quesitos e Respostas.
    - Uma única planilha 'Relatorio'
    - Colunas padronizadas (ver COLUNAS)
    """
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    df = _to_df(linhas)

    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as xl:
        df.to_excel(xl, index=False, sheet_name="Relatorio")

        # Ajuste simples de largura
        ws = xl.sheets["Relatorio"]
        for col_idx, col_name in enumerate(df.columns, start=1):
            max_len = max([len(str(col_name))] + [len(str(v)) for v in df[col_name].astype(str).tolist()])
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 2, 80)

    return caminho_saida
