import re
from typing import Tuple, Dict, Any, Iterable, List

# Padrões aceitos: <pagina> 12  |  pág. 12  |  fl. 12 / fls. 12
RE_PAG = re.compile(r"(?:<\s*pagina\s*>\s*|p[áa]g\.?\s*|fls?\.?\s*)(\d+)", re.IGNORECASE)

_CACHE_PAGINAS: Dict[int, Tuple[List[str], Dict[int, List[str]]]] = {}

def normalizar_referencia(ref: str) -> str:
    if not isinstance(ref, str):
        return ref
    m = RE_PAG.search(ref)
    if m:
        return f"<pagina> {int(m.group(1))}"
    num = re.findall(r"\d+", ref or "")
    return f"<pagina> {int(num[0])}" if num else ref

def detectar_ultima_pagina(texto: str) -> int:
    headers, paginas_dict = indexar_linhas_por_pagina(texto)
    if paginas_dict:
        return max(paginas_dict.keys())
    return 0

def indexar_linhas_por_pagina(texto: str) -> Tuple[List[str], Dict[int, List[str]]]:
    """Indexa o texto uma única vez em memória organizando linhas por número de página."""
    key = hash(texto) if len(texto) < 10000000 else id(texto)
    if key in _CACHE_PAGINAS:
        return _CACHE_PAGINAS[key]

    paginas_dict: Dict[int, List[str]] = {}
    headers: List[str] = []
    cur = 0

    for ln in (texto or "").splitlines():
        m = RE_PAG.search(ln)
        if m:
            cur = int(m.group(1))
        if cur == 0:
            headers.append(ln)
        else:
            if cur not in paginas_dict:
                paginas_dict[cur] = []
            paginas_dict[cur].append(ln)

    _CACHE_PAGINAS[key] = (headers, paginas_dict)
    return headers, paginas_dict

def slice_by_pages(texto: str, start_page: int, end_page: int, overlap_prev: int = 1) -> str:
    """Extrai o trecho correspondente às páginas [start_page, end_page] usando o índice otimizado."""
    if start_page > end_page:
        start_page, end_page = end_page, start_page
    start_eff = max(1, start_page - max(0, overlap_prev))

    headers, paginas_dict = indexar_linhas_por_pagina(texto)
    linhas = list(headers) if start_page == 1 else []

    for p in range(start_eff, end_page + 1):
        if p in paginas_dict:
            linhas.extend(paginas_dict[p])

    return "\n".join(linhas)

def maior_pagina_referenciada(indices: Dict[str, Any]) -> int:
    maxp = 0
    if not isinstance(indices, dict):
        return 0
    for item in indices.values():
        if not isinstance(item, dict):
            continue
        ref = normalizar_referencia(item.get("referencia", ""))
        m = RE_PAG.search(ref or "")
        if m:
            n = int(m.group(1))
            if n > maxp:
                maxp = n
    return maxp
