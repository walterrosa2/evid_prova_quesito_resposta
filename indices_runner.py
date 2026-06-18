from typing import Dict, Any, Tuple
from prompt_engine import run_prompt
from page_utils import slice_by_pages, maior_pagina_referenciada, normalizar_referencia

def _normalizar_indices(indices: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(indices, dict):
        return {}
    out = {}
    for k, v in indices.items():
        if not isinstance(v, dict):
            continue
        ref = normalizar_referencia(v.get("referencia", ""))
        out[k] = {
            "titulo": v.get("titulo", "").strip(),
            "resumo": v.get("resumo", "").strip(),
            "referencia": ref
        }
    return out

def identificar_indices_janela(texto_completo: str, start_page: int, end_page: int, start_key_hint: str = "1.01") -> Dict[str, Any]:
    trecho = slice_by_pages(texto_completo, start_page, end_page, overlap_prev=1)
    etapa = "ETAPA 1 – ÍNDICES TEMÁTICOS"
    funcao = f"""CONTINUAÇÃO:
- Retome a **numeração** iniciando de {start_key_hint}.
- Considere somente as páginas de {start_page} até {end_page} (com pequena sobreposição).
- Não repita itens já emitidos em respostas anteriores.
- Mantenha as mesmas regras de ETAPA 1.
"""
    resultado = run_prompt(etapa, funcao, trecho)
    # mantém o envelope (entrada_enviada, resposta_estruturada/erro)
    if "resposta_estruturada" in resultado and isinstance(resultado["resposta_estruturada"], dict):
        resultado["resposta_estruturada"] = _normalizar_indices(resultado["resposta_estruturada"])
    return resultado

def mesclar_indices(dest: Dict[str, Any], fonte: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(dest or {})
    for k, v in (fonte or {}).items():
        if k not in d:
            d[k] = v
        # se colidir, pula (ou poderia renumerar, conforme preferência)
    return d
