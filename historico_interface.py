import streamlit as st
import pandas as pd
import io
import database
import ui_premium

def gerar_excel_memoria(detalhes):
    df_provas = pd.DataFrame(detalhes.get("provas", []))
    df_quesitos = pd.DataFrame(detalhes.get("quesitos", []))
    df_respostas = pd.DataFrame(detalhes.get("respostas", []))
    
    if not df_provas.empty:
        if "numero_bloco" in df_provas.columns:
            colunas_p = ["numero_bloco", "tipo", "resumo", "referencia", "conteudo"]
            colunas_p = [c for c in colunas_p if c in df_provas.columns]
            df_provas = df_provas[colunas_p].rename(columns={"numero_bloco": "Bloco"})
    if not df_quesitos.empty:
        if "numero_bloco" in df_quesitos.columns:
            colunas_q = ["numero_bloco", "quesito"]
            colunas_q = [c for c in colunas_q if c in df_quesitos.columns]
            df_quesitos = df_quesitos[colunas_q].rename(columns={"numero_bloco": "Bloco"})
    if not df_respostas.empty:
        if "numero_bloco" in df_respostas.columns:
            colunas_r = ["numero_bloco", "quesito", "resposta_tecnica", "status_tecnico", "justificativa_tecnica", "observacoes"]
            colunas_r = [c for c in colunas_r if c in df_respostas.columns]
            df_respostas = df_respostas[colunas_r].rename(columns={"numero_bloco": "Bloco"})

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as w:
        df_provas.to_excel(w, index=False, sheet_name="Provas")
        df_quesitos.to_excel(w, index=False, sheet_name="Quesitos")
        df_respostas.to_excel(w, index=False, sheet_name="Respostas")
    
    return output.getvalue()

def mostrar_interface_historico():
    ui_premium.gradient_text("🕒 Histórico de Execuções")
    
    termo = st.text_input("🔍 Buscar execução pelo nome do processo:")
    execucoes = database.list_execucoes(termo_busca=termo)
    
    if not execucoes:
        st.info("Nenhuma execução registrada no banco de dados.")
        return
        
    for exe in execucoes:
        nome_proc = exe.get('nome_processo', '')
        data_criacao = exe.get('data_criacao', '')
        
        with st.expander(f"📁 {nome_proc} - {data_criacao}"):
            detalhes = database.get_execucao_detalhes(exe['id'])
            
            qtd_blocos = len(detalhes['blocos'])
            qtd_provas = len(detalhes['provas'])
            qtd_quesitos = len(detalhes['quesitos'])
            qtd_respostas = len(detalhes['respostas'])
            
            resumo = f"**Blocos**: {qtd_blocos} | **Provas**: {qtd_provas} | **Quesitos**: {qtd_quesitos} | **Respostas**: {qtd_respostas}"
            ui_premium.glass_card("Resumo do Processamento", resumo)
            
            if st.button(f"📊 Ver Tabelas Detalhadas", key=f"view_tab_{exe['id']}"):
                st.subheader("Provas Extraídas")
                st.dataframe(pd.DataFrame(detalhes['provas']), use_container_width=True)
                st.subheader("Quesitos Gerados")
                st.dataframe(pd.DataFrame(detalhes['quesitos']), use_container_width=True)
                st.subheader("Respostas Simuladas")
                st.dataframe(pd.DataFrame(detalhes['respostas']), use_container_width=True)
                
            excel_bytes = gerar_excel_memoria(detalhes)
            st.download_button(
                label="⬇️ Baixar Excel Estruturado",
                data=excel_bytes,
                file_name=f"relatorio_historico_{exe['id']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_excel_{exe['id']}",
                use_container_width=True
            )
