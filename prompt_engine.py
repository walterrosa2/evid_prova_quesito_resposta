# prompt_engine.py
# --------------------------------------------------------------------------------------
# Engine de prompts para as etapas da aplicação (EVIDÊNCIAS, QUESITOS, RESPOSTAS).
# - Corrige o salvamento: 'entrada_enviada' agora recebe o PROMPT FINAL MONTADO,
#   garantindo que *_prompt_enviado.txt contenha o prompt integral enviado ao Gemini.
# - Mantém: prompts dedicados por etapa via 'prompt_name' e fallback robusto.
# - Mantém: correção do NameError (usa 'texto' ao montar o prompt).
# --------------------------------------------------------------------------------------

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# --- Configuração do Gemini / Model ---
try:
    from config import GOOGLE_API_KEY as _GOOGLE_API_KEY
except Exception:
    _GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

try:
    from config import GEMINI_MODEL as _GEMINI_MODEL
except Exception:
    _GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

try:
    import google.generativeai as genai
    if _GOOGLE_API_KEY:
        genai.configure(api_key=_GOOGLE_API_KEY)
except Exception:
    genai = None  # tratado em _chamar_modelo


# --------------------------------------------------------------------------------------
# Utilidades internas
# --------------------------------------------------------------------------------------
def _resolver_caminho_prompt(prompt_name: Optional[str]) -> Tuple[Optional[Path], str]:
    avisos = []
    candidatos = []
    if prompt_name:
        nome = prompt_name if prompt_name.endswith(".txt") else f"{prompt_name}.txt"
        candidatos.append(Path("prompts") / nome)

    candidatos.append(Path("prompts") / "Prompt_V1 2406_old2.txt")
    candidatos.append(Path("prompts") / "Prompt_V1 2406.txt")
    candidatos.append(Path("Prompt_V1 2406_old2.txt"))

    for c in candidatos:
        if c.exists():
            if prompt_name and c.name != (prompt_name if prompt_name.endswith(".txt") else f"{prompt_name}.txt"):
                avisos.append(f"[prompt_engine] Usando fallback de prompt: '{c.as_posix()}'")
            return c, "\n".join(avisos)

    avisos.append("[prompt_engine] Nenhum arquivo de prompt foi encontrado nos caminhos padrão.")
    return None, "\n".join(avisos)


def _carregar_prompt_base(prompt_name: Optional[str]) -> str:
    path, avisos = _resolver_caminho_prompt(prompt_name)
    if avisos:
        print(avisos)
    if not path:
        raise FileNotFoundError(
            "Nenhum arquivo de prompt foi encontrado. "
            "Crie os arquivos por etapa em 'prompts/' (prompt_etapa_evidencias.txt, "
            "prompt_etapa_quesitos.txt, prompt_etapa_respostas.txt) "
            "ou mantenha o fallback 'Prompt_V1 2406_old2.txt'."
        )
    return path.read_text(encoding="utf-8")


def _montar_prompt_final(etapa: str, funcao: str, texto: Optional[str], prompt_base: str) -> str:
    if texto is None:
        texto = ""
    partes = [
        prompt_base,
        "",
        "## CONTEXTO DE EXECUÇÃO",
        f"- Etapa: {etapa}",
        f"- Função: {funcao}",
        "",
        "## TEXTO DE ENTRADA",
        f"{texto}",
    ]
    return "\n".join(partes).strip() + "\n"


def _limpar_code_fence(s: str) -> str:
    t = s.strip()
    if t.startswith("```"):
        if t.lower().startswith("```json"):
            t = t[len("```json"):].strip()
        else:
            t = t[3:].strip()
        if t.endswith("```"):
            t = t[:-3].strip()
    return t


def _tentar_json(clean_text: str) -> Any:
    s = _limpar_code_fence(clean_text)
    try:
        return json.loads(s)
    except Exception:
        return {"raw_text": clean_text}


def _chamar_modelo(prompt_final: str) -> Tuple[Any, str]:
    """
    Retorna (resposta_estruturada, resposta_bruta_texto)
    - resposta_estruturada: dict ou {"raw_text": "..."}
    - resposta_bruta_texto: str
    """
    if genai is None:
        print("[prompt_engine] AVISO: google.generativeai não disponível. Retornando 'raw_text' para debug.")
        return {"raw_text": prompt_final}, prompt_final  # ecoa conteúdo para teste offline

    model = genai.GenerativeModel(_GEMINI_MODEL)
    resp = model.generate_content(
        prompt_final,
        generation_config={
            "temperature": 0.2,
            "top_p": 0.9,
        }
    )

    saida = getattr(resp, "text", None)
    if not saida:
        try:
            saida = resp.candidates[0].content.parts[0].text
        except Exception:
            saida = ""

    return _tentar_json(saida or ""), (saida or "")


# --------------------------------------------------------------------------------------
# API pública
# --------------------------------------------------------------------------------------
def run_prompt(etapa: str, funcao: str, texto: Optional[str], prompt_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Executa:
      - Carrega prompt_base
      - Monta prompt_final
      - Chama o modelo
      - Retorna dict padronizado para o log_service.salvar_etapa(...):

    {
      "entrada_enviada": <PROMPT FINAL MONTADO>,           # <-- usado para *_prompt_enviado.txt
      "entrada_texto":   <texto puro do bloco>,            # útil para debug
      "resposta_estruturada": <obj dict ou {'raw_text':...}>,
      "resposta_bruta":  <string vinda do modelo sem parse>
    }
    """
    prompt_base = _carregar_prompt_base(prompt_name)
    prompt_final = _montar_prompt_final(etapa, funcao, texto, prompt_base)
    resposta_estruturada, resposta_bruta = _chamar_modelo(prompt_final)

    return {
        "entrada_enviada": prompt_final,   # <-- aqui vai o prompt integral
        "entrada_texto": texto or "",
        "resposta_estruturada": resposta_estruturada,
        "resposta_bruta": resposta_bruta
    }
