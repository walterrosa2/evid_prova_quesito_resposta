$env:PYTHONPATH = "."
if (Test-Path ".env") {
    # Carrega env (opcional, o python dotenv fará isso)
}
py -3 -m streamlit run main.py --server.port 8501 --server.address 127.0.0.1
