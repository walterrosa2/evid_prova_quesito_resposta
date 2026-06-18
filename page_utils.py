import re
from typing import Tuple, Dict, Any, Iterable

# Padrões aceitos: <pagina> 12  |  pág. 12  |  fl. 12 / fls. 12
RE_PAG = re.compile(r"(?:<\s*pagina\s*>\s*|p[áa]g\.?\s*|fls?\.?\s*)(\d+)", re.IGNORECASE)

def normalizar_referencia(ref: str) -> str:
    if not isinstance(ref, str):
        return ref
    m = RE_PAG.search(ref)
    if m:
        return f"<pagina> {int(m.group(1))}"
    # tenta capturar qualquer número isolado como último recurso
    num = re.findall(r"\d+", ref or "")
    return f"<pagina> {int(num[0])}" if num else ref

def detectar_ultima_pagina(texto: str) -> int:
    # varre todas as ocorrências para capturar a maior página referenciada no texto bruto
    maxp = 0
    for m in RE_PAG.finditer(texto or ""):
        n = int(m.group(1))
        if n > maxp:
            maxp = n
    return maxp

def _iter_linhas_com_pagina(texto: str) -> Iterable[Tuple[int, str]]:
    """Rastreia a 'página corrente' ao ler o texto linha a linha."""
    cur = 0
    for ln in (texto or "").splitlines():
        m = RE_PAG.search(ln)
        if m:
            cur = int(m.group(1))
        yield cur, ln

def slice_by_pages(texto: str, start_page: int, end_page: int, overlap_prev: int = 1) -> str:
    """Extrai o trecho correspondente às páginas [start_page, end_page], com sobreposição reversa opcional."""
    if start_page > end_page:
        start_page, end_page = end_page, start_page
    start_eff = max(1, start_page - max(0, overlap_prev))
    linhas = []
    for cur, ln in _iter_linhas_com_pagina(texto):
        if cur == 0 and not linhas:
            # antes do primeiro marcador de página, inclui como cabeçalho
            linhas.append(ln)
        elif start_eff <= cur <= end_page:
            linhas.append(ln)
        elif cur > end_page and linhas:
            break
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
