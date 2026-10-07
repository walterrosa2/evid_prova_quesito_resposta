@echo off
set PYTHONPATH=.
py -3 -m streamlit run main.py --server.port 8501 --server.address 127.0.0.1
