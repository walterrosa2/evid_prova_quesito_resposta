import os
import json
from datetime import datetime

def criar_pasta_execucao(nome_processo: str, base_dir="execucoes") -> str:
    nome_limpo = nome_processo.strip().replace(" ", "_").upper()
    pasta_exec = os.path.join(base_dir, nome_limpo)
    os.makedirs(pasta_exec, exist_ok=True)
    return pasta_exec

def salvar_arquivo(nome_arquivo: str, conteudo, pasta_destino: str):
    caminho = os.path.join(pasta_destino, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        if isinstance(conteudo, (dict, list)):
            f.write(json.dumps(conteudo, indent=2, ensure_ascii=False))
        else:
            f.write(str(conteudo))

def salvar_json(nome_arquivo: str, dados, pasta_destino: str):
    caminho = os.path.join(pasta_destino, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        try:
            if not isinstance(dados, (dict, list)):
                # 🔹 Se não for JSON válido, empacotamos
                dados = {"erro": "Resposta inválida", "conteudo": str(dados)}
            json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # 🔹 Fallback: salvar como texto mesmo assim
            f.write(json.dumps({"erro": f"Falha ao salvar JSON: {e}", "conteudo": str(dados)}, ensure_ascii=False))

def salvar_etapa(etapa: str, texto_input: str, resposta: dict, pasta_execucao: str):
    salvar_arquivo(f"{etapa}_prompt_enviado.txt", texto_input, pasta_execucao)

    # ✅ Sempre salvar no mesmo formato
    if "resposta_estruturada" in resposta and isinstance(resposta["resposta_estruturada"], dict):
        dados = {"resposta_estruturada": resposta["resposta_estruturada"]}
    elif "resposta_bruta" in resposta:
        dados = {"resposta_bruta": resposta["resposta_bruta"]}
    else:
        dados = {"resposta_estruturada": resposta}  # força o encapsulamento

    salvar_json(f"{etapa}_resposta.json", dados, pasta_execucao)


if __name__ == "__main__":
    pasta = criar_pasta_execucao("PROCESSO_TESTE")
    salvar_etapa(
        etapa="provas_bloco_01",
        texto_input="Trecho de exemplo do processo",
        resposta={"exemplo": "resposta da IA"},
        pasta_execucao=pasta
    )
