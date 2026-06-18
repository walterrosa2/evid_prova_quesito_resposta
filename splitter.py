def dividir_blocos(texto: str, janela_paginas: int = 100, sobreposicao: int = 1, max_tokens: int = 100000) -> list:
    import tiktoken
    from page_utils import detectar_ultima_pagina, slice_by_pages

    enc = tiktoken.get_encoding("cl100k_base")
    total_tokens = len(enc.encode(texto))
    last_page = detectar_ultima_pagina(texto)

    # 🔹 Se não há marcações de página, usar divisão por tokens (modo antigo)
    if last_page <= 0:
        if total_tokens <= max_tokens:
            return [{"texto": texto, "tokens": total_tokens}]
        palavras = texto.split("\n")
        blocos, bloco_atual, tokens_atual = [], [], 0
        for linha in palavras:
            if not linha.strip():
                continue
            tokens_linha = len(enc.encode(linha))
            if tokens_atual + tokens_linha <= max_tokens:
                bloco_atual.append(linha)
                tokens_atual += tokens_linha
            else:
                blocos.append({"texto": "\n".join(bloco_atual), "tokens": tokens_atual})
                bloco_atual, tokens_atual = [linha], tokens_linha
        if bloco_atual:
            blocos.append({"texto": "\n".join(bloco_atual), "tokens": tokens_atual})
        return blocos

    # 🔹 Divisão principal por faixas de páginas
    blocos = []
    start = 1
    while start <= last_page:
        end = min(start + janela_paginas - 1, last_page)
        trecho = slice_by_pages(texto, start, end, overlap_prev=sobreposicao)

        tokens = len(enc.encode(trecho))
        # ⚠️ ignora blocos minúsculos
        if tokens < 100:
            start = end + 1
            continue

        blocos.append({
            "texto": trecho,
            "tokens": tokens,
            "start_page": start,
            "end_page": end
        })
        start = end + 1

    # ⚠️ fallback extra se todos blocos ficarem minúsculos
    if not blocos:
        blocos = [{"texto": texto, "tokens": total_tokens}]
    return blocos
