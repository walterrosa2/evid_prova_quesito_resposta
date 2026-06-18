import json
import os

def carregar_indices(caminho_arquivo):
    """Carrega um arquivo de índices, independentemente do formato."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler {caminho_arquivo}: {e}")
        return {}

    # Caso 1: formato resposta_bruta (texto JSON dentro de string)
    if "resposta_bruta" in data:
        try:
            bruto = json.loads(data["resposta_bruta"])
            if "estrutura_saida" in bruto:
                return bruto["estrutura_saida"]
            elif "resposta_estruturada" in bruto:
                return bruto["resposta_estruturada"]
            else:
                return bruto
        except Exception as e:
            print(f"⚠️ Erro ao interpretar resposta_bruta em {caminho_arquivo}: {e}")
            return {}

    # Caso 2: formato resposta_estruturada (já em dict)
    if "resposta_estruturada" in data:
        return data["resposta_estruturada"]

    # Caso 3: já plano
    if isinstance(data, dict):
        return data

    return {}

def merge_indices(lista_arquivos, arquivo_saida="indices_consolidados.json"):
    """Mescla vários arquivos de índices em um único JSON consolidado."""
    indices_merged = {}
    for caminho in lista_arquivos:
        bloc = carregar_indices(caminho)
        for k, v in bloc.items():
            if k not in indices_merged:
                indices_merged[k] = v
            else:
                print(f"⚠️ Chave duplicada ignorada: {k} (arquivo {caminho})")

    # Ordenar por código (1.01, 1.02, 2.00...)
    try:
        indices_ordenados = dict(sorted(
            indices_merged.items(),
            key=lambda x: list(map(int, x[0].split(".")))
        ))
    except Exception:
        indices_ordenados = indices_merged

    consolidado = {"resposta_estruturada": indices_ordenados}

    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(consolidado, f, ensure_ascii=False, indent=2)

    print(f"✅ Arquivo consolidado salvo em: {arquivo_saida}")
    print(f"Total de itens consolidados: {len(indices_ordenados)}")
    return consolidado


if __name__ == "__main__":
    # Ajuste os nomes conforme os arquivos disponíveis
    arquivos = [
        "indices_bloco_01_resposta.json",
        "indices_bloco_02_resposta.json",
        "indices_bloco_03_resposta.json"
    ]
    merge_indices(arquivos, "indices_consolidados.json")
