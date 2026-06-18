# evid_app/upload_interface.py

import streamlit as st

def carregar_texto():
    uploaded_file = st.file_uploader("📤 Envie o arquivo do processo (formato .txt)", type=["txt"])
    if uploaded_file is not None:
        try:
            # Tenta decodificar como UTF-8
            texto = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            # Se falhar, tenta ISO-8859-1 (Windows padrão)
            uploaded_file.seek(0)
            texto = uploaded_file.read().decode("iso-8859-1")
        return texto
    return None