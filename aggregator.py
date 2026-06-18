# aggregator.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _safe_dump(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)

def _linhas_provas(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Esperado:
    {
      "resposta_estruturada": {
         "1.01": [ { "tipo": "...", "conteudo": "...", "resumo": "...", "referencia": "fls. X" }, ...],
         ...
      }
    }
    """
    linhas = []
    blocos = obj.get("resposta_estruturada", {})
    for indice, itens in blocos.items():
        for it in (itens or []):
            linhas.append({
                "Indice": indice,
                "Categoria": "Prova",
                "TipoProva": it.get("tipo", ""),
                "Resumo": it.get("resumo", ""),
                "Referencia": it.get("referencia", ""),
                "Quesito": "",
                "RespostaTecnica": "",
                "StatusTecnico": "",
                "JustificativaTecnica": "",
                "Observacoes": "",
                "Conteudo": _safe_dump(it),  # bruto
            })
    return linhas

def _linhas_quesitos(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Esperado:
    {
      "resposta_estruturada": {
         "1.01": ["Q1", "Q2", ...],
         ...
      }
    }
    """
    linhas = []
    blocos = obj.get("resposta_estruturada", {})
    for indice, lista in blocos.items():
        for q in (lista or []):
            linhas.append({
                "Indice": indice,
                "Categoria": "Quesito",
                "TipoProva": "",
                "Resumo": "",
                "Referencia": "",
                "Quesito": q,
                "RespostaTecnica": "",
                "StatusTecnico": "",
                "JustificativaTecnica": "",
                "Observacoes": "",
                "Conteudo": _safe_dump(q),
            })
    return linhas

def _linhas_respostas(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Esperado:
    {
      "resposta_estruturada": {
        "estrutura_resposta": {
          "1.01": [ { "quesito": "...",
                      "resposta_tecnica": "...",
                      "status_tecnico": "...",
                      "justificativa_tecnica": "...",
                      "observacoes_adicionais": null }, ... ],
          ...
        }
      }
    }
    """
    linhas = []
    raiz = obj.get("resposta_estruturada", {})
    estrutura = raiz.get("estrutura_resposta", raiz)   # fallback: se já vier "achatado"
    for indice, lista in estrutura.items():
        for it in (lista or []):
            linhas.append({
                "Indice": indice,
                "Categoria": "Resposta",
                "TipoProva": "",
                "Resumo": "",
                "Referencia": "",
                "Quesito": it.get("quesito", ""),
                "RespostaTecnica": it.get("resposta_tecnica", ""),
                "StatusTecnico": it.get("status_tecnico", ""),
                "JustificativaTecnica": it.get("justificativa_tecnica", ""),
                "Observacoes": it.get("observacoes_adicionais", ""),
                "Conteudo": _safe_dump(it),
            })
    return linhas

def agregar_linhas(
    caminho_provas: Path | None,
    caminho_quesitos: Path | None,
    caminho_respostas: Path | None
) -> List[Dict[str, Any]]:
    """
    Retorna lista de linhas normalizadas para o Excel.
    """
    linhas: List[Dict[str, Any]] = []

    if caminho_provas and Path(caminho_provas).exists():
        linhas.extend(_linhas_provas(_load_json(Path(caminho_provas))))

    if caminho_quesitos and Path(caminho_quesitos).exists():
        linhas.extend(_linhas_quesitos(_load_json(Path(caminho_quesitos))))

    if caminho_respostas and Path(caminho_respostas).exists():
        linhas.extend(_linhas_respostas(_load_json(Path(caminho_respostas))))

    # Ordena por Indice e Categoria para uma leitura melhor
    cat_ordem = {"Prova": 0, "Quesito": 1, "Resposta": 2}
    linhas.sort(key=lambda r: (r.get("Indice", ""), cat_ordem.get(r.get("Categoria", ""), 99)))
    return linhas
