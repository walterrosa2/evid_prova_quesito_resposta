import streamlit as st
import os

def apply_premium_style():
    """Injeta CSS premium, fontes e reset de estilos no Streamlit."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@400;700&display=swap');

        /* Cores base */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #0E1117 !important;
            color: #FFFFFF !important;
        }

        /* Garante que todo o texto normal fique branco no fundo escuro */
        p, span, label, li, .stMarkdown {
            color: #E2E8F0 !important;
        }

        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            color: #00D1FF !important;
        }

        /* Ajustes sutis para botões */
        .stButton>button {
            border-radius: 8px;
            border: 1px solid rgba(0, 209, 255, 0.3);
            background: rgba(0, 209, 255, 0.05) !important;
            color: #00D1FF !important;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background: #00D1FF !important;
            color: #0E1117 !important;
            box-shadow: 0 0 15px rgba(0, 209, 255, 0.4);
        }

        /* Glassmorphism Card */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin: 10px 0;
            color: #FFFFFF;
            transition: transform 0.2s ease;
        }

        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0, 209, 255, 0.3);
        }

        /* Ajuste de Contrastes: Inputs, Textareas e Dataframes */
        input, textarea, .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            color: #FFFFFF !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }

        /* Gradient Text */
        .gradient-text {
            background: linear-gradient(90deg, #00D1FF 0%, #00FFA3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        /* Ajuste do Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(22, 27, 34, 0.8) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Dataframes base */
        .dataframe, .dataframe th, .dataframe td {
            background-color: transparent !important;
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

def glass_card(title, content):
    """Renderiza um card com efeito Glassmorphism."""
    st.markdown(f"""
        <div class="glass-card">
            <h3 style="margin-top:0;">{title}</h3>
            <div>{content}</div>
        </div>
    """, unsafe_allow_html=True)

def gradient_text(text, level="h1"):
    """Gera texto gradiente em um cabeçalho específico."""
    st.markdown(f"<{level} class='gradient-text'>{text}</{level}>", unsafe_allow_html=True)

def set_premium_config():
    """Gera o arquivo config.toml se ele não existir."""
    config_path = ".streamlit/config.toml"
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    
    config_content = """
[theme]
primaryColor = "#00D1FF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#161B22"
textColor = "#FFFFFF"
font = "sans serif"

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
"""
    # Só sobrescreve se o arquivo não existir
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(config_content.strip())
