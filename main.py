# Deve ser a PRIMEIRA chamada Streamlit no script, antes de qualquer st.write/st.sidebar/etc.
import streamlit as st

st.set_page_config(
    page_title="EVID - Provas e Quesitos",   # <- era 'title'
    page_icon=":mag:",                        # opcional
    layout="wide",
    initial_sidebar_state="expanded"          # opcional
)

import os
import json
import time
from pathlib import Path
import streamlit as st
import json
import pandas as pd


from evidence_mapper import mapear_provas
from quesito_generator import gerar_quesitos
from resposta_simulator import simular_respostas

# Módulos utilitários existentes no projeto (mantidos)
from upload_interface import carregar_texto
from splitter import dividir_blocos
from log_service import criar_pasta_execucao, salvar_etapa
from aggregator import agregar_linhas
from report_generator import exportar_excel
from historico_interface import mostrar_interface_historico
from aggregator import agregar_linhas
from config import get_exec_path

import database
import ui_premium

# Inicialização da persistência e estilo premium
database.init_db()
ui_premium.apply_premium_style()

def _load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def _df_provas(obj, bloco_label):
    import pandas as pd
    linhas = []
    blocos = (obj or {}).get("resposta_estruturada", {})
    for indice, itens in blocos.items():
        for it in (itens or []):
            linhas.append({
                "Bloco": bloco_label,
                "Indice": indice,
                "TipoProva": it.get("tipo", ""),
                "Resumo": it.get("resumo", ""),
                "Referencia": it.get("referencia", ""),
                "Conteudo": it.get("conteudo", ""),
            })
    return pd.DataFrame(linhas, columns=["Bloco","Indice","TipoProva","Resumo","Referencia","Conteudo"])

def _df_quesitos(obj, bloco_label):
    import pandas as pd
    linhas = []
    blocos = (obj or {}).get("resposta_estruturada", {})
    for indice, lista in blocos.items():
        for q in (lista or []):
            linhas.append({"Bloco": bloco_label, "Indice": indice, "Quesito": q})
    return pd.DataFrame(linhas, columns=["Bloco","Indice","Quesito"])

def _df_respostas(obj, bloco_label):
    import pandas as pd
    linhas = []
    raiz = (obj or {}).get("resposta_estruturada", {})
    estrutura = raiz.get("estrutura_resposta", raiz)  # fallback compatível
    for indice, lista in estrutura.items():
        for it in (lista or []):
            linhas.append({
                "Bloco": bloco_label,
                "Indice": indice,
                "Quesito": it.get("quesito", ""),
                "RespostaTecnica": it.get("resposta_tecnica", ""),
                "StatusTecnico": it.get("status_tecnico", ""),
                "JustificativaTecnica": it.get("justificativa_tecnica", ""),
                "Observacoes": it.get("observacoes_adicionais", ""),
            })
    return pd.DataFrame(linhas, columns=[
        "Bloco","Indice","Quesito","RespostaTecnica","StatusTecnico","JustificativaTecnica","Observacoes"
    ])

def _ajustar_ordem(df, cols):
    if df is None or df.empty: 
        return df
    fix = [c for c in cols if c in df.columns]
    rest = [c for c in df.columns if c not in fix]
    return df[fix + rest]



# --------------------------
# helpers locais
# --------------------------
def exibir_json_seguro(data, label="Pré-visualização da saída"):
    try:
        if isinstance(data, dict) and "resposta_estruturada" in data:
            st.json(data["resposta_estruturada"])
        elif isinstance(data, dict) and "resposta_bruta" in data:
            st.text_area(label, str(data["resposta_bruta"]), height=250)
        else:
            st.json(data)
    except Exception:
        st.text_area(label, str(data), height=250)

def _carregar_json(caminho: str):
    if not caminho or not os.path.exists(caminho):
        return None
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def buscar_arquivo_mais_recente(prefixo_nome: str, pasta_execucao: str):
    """Retorna o caminho do arquivo mais recente na pasta que contenha o prefixo informado."""
    candidatos = [os.path.join(pasta_execucao, f) for f in os.listdir(pasta_execucao) if prefixo_nome in f and f.endswith(".json")]
    if not candidatos:
        return None
    candidatos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidatos[0]

def _root_exec_base() -> Path:
    """Raiz de execuções do dia (caso queira aproveitar em automações externas)."""
    return Path("execucoes") / time.strftime("%Y%m%d")


# --------------------------
# execução em lote 2→3→4
# --------------------------
def executar_todas_as_etapas(nome_processo: str, texto_completo: str, blocos: list[dict], pasta_execucao: str, reprocessar: bool = False) -> dict:
    """
    Executa, em sequência, Provas -> Quesitos -> Respostas para TODOS os blocos.
    Também persiste os resultados no SQLite a cada bloco concluído.
    """
    out = {"provas": [], "quesitos": [], "respostas": []}
    total = max(1, len(blocos) * 3)
    progresso = st.progress(0)
    passo = 0
    
    st.info(f"O documento possui {len(blocos)} blocos. Total de subetapas: {total}.")
    log_container = st.empty()
    
    # Inicia a execução no banco de dados
    exec_id = database.insert_execucao(nome_processo, texto_completo)

    for i, bloco in enumerate(blocos):
        bloco_id = f"{i+1:02d}"
        texto_bloco = bloco.get("texto", "") or ""

        # ---------- ETAPA 2: PROVAS ----------
        nome_provas = f"provas_bloco_{bloco_id}_resposta.json"
        caminho_existente = buscar_arquivo_mais_recente(nome_provas, pasta_execucao)
        if not caminho_existente or reprocessar:
            with st.spinner(f"🧩 [Bloco {bloco_id}] Mapeando PROVAS…"):
                provas = mapear_provas(texto_bloco)  # sem índices; usa GERAL
                salvar_etapa(f"provas_bloco_{bloco_id}", provas.get("entrada_enviada", texto_bloco), provas, pasta_execucao)
                out["provas"].append(os.path.join(pasta_execucao, nome_provas))
                st.success(f"✅ PROVAS geradas (Bloco {bloco_id})")
        else:
            st.info(f"🧩 [Bloco {bloco_id}] PROVAS já existentes — pulando. Ative 'Reprocessar' para refazer.")
            out["provas"].append(caminho_existente)
            provas = _carregar_json(caminho_existente) or {}
        passo += 1
        progresso.progress(min(passo / total, 1.0))

        # ---------- ETAPA 3: QUESITOS ----------
        nome_quesitos = f"quesitos_bloco_{bloco_id}_resposta.json"
        caminho_q_existente = buscar_arquivo_mais_recente(nome_quesitos, pasta_execucao)
        if not caminho_q_existente or reprocessar:
            with st.spinner(f"📝 [Bloco {bloco_id}] Gerando QUESITOS…"):
                quesitos = gerar_quesitos(texto_bloco, evidencias=provas)
                salvar_etapa(f"quesitos_bloco_{bloco_id}", quesitos.get("entrada_enviada", texto_bloco), quesitos, pasta_execucao)
                out["quesitos"].append(os.path.join(pasta_execucao, nome_quesitos))
                st.success(f"✅ QUESITOS gerados (Bloco {bloco_id})")
        else:
            st.info(f"📝 [Bloco {bloco_id}] QUESITOS já existentes — pulando. Ative 'Reprocessar' para refazer.")
            out["quesitos"].append(caminho_q_existente)
            quesitos = _carregar_json(caminho_q_existente) or {}
        passo += 1
        progresso.progress(min(passo / total, 1.0))

        # ---------- ETAPA 4: RESPOSTAS ----------
        nome_respostas = f"respostas_bloco_{bloco_id}_resposta.json"
        caminho_r_existente = buscar_arquivo_mais_recente(nome_respostas, pasta_execucao)
        if not caminho_r_existente or reprocessar:
            with st.spinner(f"⚖️ [Bloco {bloco_id}] Simulando RESPOSTAS…"):
                respostas = simular_respostas(quesitos=quesitos, evidencias=provas, contexto_opcional=texto_bloco)
                salvar_etapa(f"respostas_bloco_{bloco_id}", respostas.get("entrada_enviada", ""), respostas, pasta_execucao)
                out["respostas"].append(os.path.join(pasta_execucao, nome_respostas))
                st.success(f"✅ RESPOSTAS geradas (Bloco {bloco_id})")
        else:
            st.info(f"⚖️ [Bloco {bloco_id}] RESPOSTAS já existentes — pulando. Ative 'Reprocessar' para refazer.")
            out["respostas"].append(caminho_r_existente)
        passo += 1
        progresso.progress(min(passo / total, 1.0))
        
        # Salva o bloco e todos os dados associados no banco de dados
        try:
            database.insert_bloco_completo(
                execucao_id=exec_id, 
                numero_bloco=i+1, 
                conteudo_texto=texto_bloco, 
                provas=provas, 
                quesitos=quesitos, 
                respostas=respostas
            )
            log_container.success(f"💾 Bloco {bloco_id} processado e salvo no banco de dados.")
        except Exception as e:
            st.error(f"Erro ao salvar bloco {bloco_id} no banco: {e}")

    st.success("Lote concluído com sucesso e persistido no banco de dados! ✅")
    return out


# --------------------------
# UI
# --------------------------
#st.set_page_config(page_title="EVID - Provas e Quesitos", layout="wide")

st.sidebar.title("EVID – Provas e Quesitos")
menu = st.sidebar.radio("Menu", ["Nova Análise", "Histórico de Execuções"])

if menu == "Nova Análise":
    st.header("🚀 Nova Análise (Etapas 2, 3 e 4)")
    nome_processo = st.text_input("Nome do processo", value="PROCESSO TESTE")
    texto = carregar_texto()  # componente existente

    if texto:
        blocos = dividir_blocos(texto)
        st.info(f"Texto carregado. {len(blocos)} bloco(s) identificado(s).")
        pasta_execucao = criar_pasta_execucao(nome_processo)
        # Guarde o nome da execução na sessão (usaremos no botão do Excel)
        from pathlib import Path
        st.session_state["nome_execucao"] = Path(pasta_execucao).name


        # BOTÃO ÚNICO – executa 2→3→4 para todos os blocos
        with st.expander("🚀 Executar TODAS as etapas (2→3→4)"):
            col_run1, col_run2 = st.columns([1, 1])
            reprocessar = col_run1.checkbox("Reprocessar (sobrescrever saídas existentes)?", value=False)
            if col_run2.button("▶️ Executar todas as etapas agora"):
                resultado_lote = executar_todas_as_etapas(nome_processo, texto, blocos, pasta_execucao, reprocessar=reprocessar)
                st.json(resultado_lote)

        st.markdown("---")

        # Botões de atalho para processar tudo por ETAPA (mantidos)
        col_all1, col_all2, col_all3 = st.columns(3)
        with col_all1:
            if st.button("📎 Executar PROVAS para todos os blocos"):
                for i, bloco in enumerate(blocos):
                    resultado = mapear_provas(bloco["texto"])
                    salvar_etapa(f"provas_bloco_{i+1:02d}", resultado.get("entrada_enviada", bloco["texto"]), resultado, pasta_execucao)
                st.success("✅ Provas geradas para todos os blocos.")
        with col_all2:
            if st.button("📝 Executar QUESITOS para todos os blocos"):
                for i, bloco in enumerate(blocos):
                    nome_p = f"provas_bloco_{i+1:02d}_resposta.json"
                    caminho_p = buscar_arquivo_mais_recente(nome_p, pasta_execucao)
                    evidencias = _carregar_json(caminho_p) or {}
                    resultado = gerar_quesitos(bloco["texto"], evidencias=evidencias)
                    salvar_etapa(f"quesitos_bloco_{i+1:02d}", resultado.get("entrada_enviada", bloco["texto"]), resultado, pasta_execucao)
                st.success("✅ Quesitos gerados para todos os blocos.")
        with col_all3:
            if st.button("⚖️ Executar RESPOSTAS para todos os blocos"):
                for i, bloco in enumerate(blocos):
                    nome_p = f"provas_bloco_{i+1:02d}_resposta.json"
                    nome_q = f"quesitos_bloco_{i+1:02d}_resposta.json"
                    caminho_p = buscar_arquivo_mais_recente(nome_p, pasta_execucao)
                    caminho_q = buscar_arquivo_mais_recente(nome_q, pasta_execucao)
                    evidencias = _carregar_json(caminho_p) or {}
                    quesitos   = _carregar_json(caminho_q) or {}
                    resultado = simular_respostas(quesitos, evidencias, contexto_opcional=bloco["texto"])
                    salvar_etapa(f"respostas_bloco_{i+1:02d}", resultado.get("entrada_enviada", ""), resultado, pasta_execucao)
                st.success("✅ Respostas geradas para todos os blocos.")

        st.markdown("---")

        # Blocos individuais
        for i, bloco in enumerate(blocos):
            with st.expander(f"🧩 Bloco {i+1} ({bloco['tokens']} tokens)"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(f"📎 Provas (Bloco {i+1})"):
                        with st.spinner("⏳ Mapeando evidências..."):
                            resultado = mapear_provas(bloco["texto"])
                            salvar_etapa(f"provas_bloco_{i+1:02d}", resultado.get("entrada_enviada", bloco["texto"]), resultado, pasta_execucao)
                            st.success("✅ Provas mapeadas!")
                            exibir_json_seguro(resultado)

                with col2:
                    if st.button(f"📝 Quesitos (Bloco {i+1})"):
                        with st.spinner("⏳ Gerando quesitos..."):
                            nome_p = f"provas_bloco_{i+1:02d}_resposta.json"
                            caminho_p = buscar_arquivo_mais_recente(nome_p, pasta_execucao)
                            evidencias = _carregar_json(caminho_p) or {}
                            resultado = gerar_quesitos(bloco["texto"], evidencias=evidencias)
                            salvar_etapa(f"quesitos_bloco_{i+1:02d}", resultado.get("entrada_enviada", bloco["texto"]), resultado, pasta_execucao)
                            st.success("✅ Quesitos gerados!")
                            exibir_json_seguro(resultado)

                with col3:
                    if st.button(f"⚖️ Respostas (Bloco {i+1})"):
                        with st.spinner("⏳ Simulando respostas..."):
                            nome_p = f"provas_bloco_{i+1:02d}_resposta.json"
                            nome_q = f"quesitos_bloco_{i+1:02d}_resposta.json"
                            caminho_p = buscar_arquivo_mais_recente(nome_p, pasta_execucao)
                            caminho_q = buscar_arquivo_mais_recente(nome_q, pasta_execucao)
                            evidencias = _carregar_json(caminho_p) or {}
                            quesitos   = _carregar_json(caminho_q) or {}
                            resultado = simular_respostas(quesitos, evidencias, contexto_opcional=bloco["texto"])
                            salvar_etapa(f"respostas_bloco_{i+1:02d}", resultado.get("entrada_enviada", ""), resultado, pasta_execucao)
                            st.success("✅ Respostas geradas!")
                            exibir_json_seguro(resultado)

        st.subheader("📤 Exportar Relatório Final")
        # Ajuste o label do botão
    if st.button("📁 Gerar Excel", type="primary", use_container_width=True):
        # 1) Nome/pasta da execução a partir da sessão (preenchida quando criamos a pasta)
        nome_execucao = st.session_state.get("nome_execucao", "").strip()

        if not nome_execucao:
            st.error("Nome da execução não encontrado. Gere as etapas (ou informe a execução) antes de exportar o Excel.")
            st.stop()

        # 2) Pasta real da execução (usa a fonte-da-verdade do config.py)
        from config import get_exec_path
        base_exec = get_exec_path(nome_execucao)

        if not base_exec.exists():
            st.error(f"Pasta da execução não encontrada: {base_exec}")
            st.stop()

        # 3) Varredura RECURSIVA (cobre subpastas)
        provas_files    = sorted(base_exec.rglob("provas_bloco_*_resposta.json"))
        quesitos_files  = sorted(base_exec.rglob("quesitos_bloco_*_resposta.json"))
        respostas_files = sorted(base_exec.rglob("respostas_bloco_*_resposta.json"))

        # Diagnóstico útil na UI
        st.caption(f"🔎 Procurando arquivos em: {base_exec}")
        st.write({
            "provas_encontrados": len(provas_files),
            "quesitos_encontrados": len(quesitos_files),
            "respostas_encontrados": len(respostas_files),
        })

        if not (provas_files or quesitos_files or respostas_files):
            st.error("Nenhum JSON de saída encontrado nessa pasta.")
            st.stop()

        # 4) Monta DataFrames por aba
        dfs_provas = []
        for p in provas_files:
            bloco = p.stem.replace("_resposta","").replace("provas_","").replace("bloco_","Bloco ")
            dfs_provas.append(_df_provas(_load_json(p), bloco))
        df_provas = pd.concat(dfs_provas, ignore_index=True) if dfs_provas else pd.DataFrame(columns=["Bloco","Indice","TipoProva","Resumo","Referencia","Conteudo"])

        dfs_quesitos = []
        for p in quesitos_files:
            bloco = p.stem.replace("_resposta","").replace("quesitos_","").replace("bloco_","Bloco ")
            dfs_quesitos.append(_df_quesitos(_load_json(p), bloco))
        df_quesitos = pd.concat(dfs_quesitos, ignore_index=True) if dfs_quesitos else pd.DataFrame(columns=["Bloco","Indice","Quesito"])

        dfs_respostas = []
        for p in respostas_files:
            bloco = p.stem.replace("_resposta","").replace("respostas_","").replace("bloco_","Bloco ")
            dfs_respostas.append(_df_respostas(_load_json(p), bloco))
        df_respostas = pd.concat(dfs_respostas, ignore_index=True) if dfs_respostas else pd.DataFrame(columns=["Bloco","Indice","Quesito","RespostaTecnica","StatusTecnico","JustificativaTecnica","Observacoes"])

        # 5) Remover coluna 'Indice' (conforme sua decisão)
        for _df in (df_provas, df_quesitos, df_respostas):
            if not _df.empty and "Indice" in _df.columns:
                _df.drop(columns=["Indice"], inplace=True)

        # 6) Ordenar colunas e salvar SOMENTE as 3 abas
        df_provas    = _ajustar_ordem(df_provas,    ["Bloco","TipoProva","Resumo","Referencia","Conteudo"])
        df_quesitos  = _ajustar_ordem(df_quesitos,  ["Bloco","Quesito"])
        df_respostas = _ajustar_ordem(df_respostas, ["Bloco","Quesito","RespostaTecnica","StatusTecnico","JustificativaTecnica","Observacoes"])

        saida_excel = base_exec / "relatorio_final.xlsx"
        with pd.ExcelWriter(saida_excel, engine="openpyxl") as w:
            df_provas.to_excel(w, index=False, sheet_name="Provas")
            df_quesitos.to_excel(w, index=False, sheet_name="Quesitos")
            df_respostas.to_excel(w, index=False, sheet_name="Respostas")

        st.success(f"Excel gerado: {saida_excel}")
        st.download_button(
            "⬇️ Baixar Excel",
            data=saida_excel.read_bytes(),
            file_name=saida_excel.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

elif menu == "Histórico de Execuções":
    mostrar_interface_historico()
