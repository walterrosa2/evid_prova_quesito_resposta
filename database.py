import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

DB_NAME = "evid_provas.db"

def get_connection():
    # Retorna uma conexão SQLite com a habilidade de tratar dicionários (Row)
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados SQLite caso não existam."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela: execucoes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_processo TEXT NOT NULL,
                data_criacao TEXT NOT NULL,
                texto_completo TEXT
            )
        """)
        
        # Tabela: blocos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execucao_id INTEGER NOT NULL,
                numero_bloco INTEGER NOT NULL,
                conteudo_texto TEXT,
                FOREIGN KEY (execucao_id) REFERENCES execucoes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela: provas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS provas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bloco_id INTEGER NOT NULL,
                indice TEXT,
                tipo TEXT,
                resumo TEXT,
                referencia TEXT,
                conteudo TEXT,
                FOREIGN KEY (bloco_id) REFERENCES blocos(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela: quesitos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quesitos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bloco_id INTEGER NOT NULL,
                indice TEXT,
                quesito TEXT,
                FOREIGN KEY (bloco_id) REFERENCES blocos(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela: respostas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bloco_id INTEGER NOT NULL,
                indice TEXT,
                quesito TEXT,
                resposta_tecnica TEXT,
                status_tecnico TEXT,
                justificativa_tecnica TEXT,
                observacoes TEXT,
                FOREIGN KEY (bloco_id) REFERENCES blocos(id) ON DELETE CASCADE
            )
        """)
        
        # Criação de Índices (Ignora se já existir usando o padrão de try/except caso a versão do SQLite não suporte IF NOT EXISTS no index)
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_execucoes_nome ON execucoes(nome_processo)",
            "CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_criacao)",
            "CREATE INDEX IF NOT EXISTS idx_blocos_execucao ON blocos(execucao_id)",
            "CREATE INDEX IF NOT EXISTS idx_provas_bloco ON provas(bloco_id)",
            "CREATE INDEX IF NOT EXISTS idx_quesitos_bloco ON quesitos(bloco_id)",
            "CREATE INDEX IF NOT EXISTS idx_respostas_bloco ON respostas(bloco_id)"
        ]
        for idx_query in indices:
            cursor.execute(idx_query)
            
        conn.commit()

def insert_execucao(nome_processo: str, texto_completo: str) -> int:
    """Insere uma nova execução no banco de dados e retorna seu ID."""
    data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO execucoes (nome_processo, data_criacao, texto_completo) VALUES (?, ?, ?)",
            (nome_processo, data_criacao, texto_completo)
        )
        conn.commit()
        return cursor.lastrowid

def insert_bloco_completo(execucao_id: int, numero_bloco: int, conteudo_texto: str, provas: dict, quesitos: dict, respostas: dict):
    """
    Insere o bloco e seus sub-itens extraídos na mesma transação.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Insere Bloco
        cursor.execute(
            "INSERT INTO blocos (execucao_id, numero_bloco, conteudo_texto) VALUES (?, ?, ?)",
            (execucao_id, numero_bloco, conteudo_texto)
        )
        bloco_id = cursor.lastrowid
        
        # Extrai e Insere Provas
        blocos_provas = (provas or {}).get("resposta_estruturada", {})
        for indice, itens in blocos_provas.items():
            for it in (itens or []):
                cursor.execute("""
                    INSERT INTO provas (bloco_id, indice, tipo, resumo, referencia, conteudo) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    bloco_id, str(indice), it.get("tipo", ""), it.get("resumo", ""), 
                    it.get("referencia", ""), it.get("conteudo", "")
                ))
        
        # Extrai e Insere Quesitos
        blocos_quesitos = (quesitos or {}).get("resposta_estruturada", {})
        for indice, lista in blocos_quesitos.items():
            for q in (lista or []):
                cursor.execute(
                    "INSERT INTO quesitos (bloco_id, indice, quesito) VALUES (?, ?, ?)",
                    (bloco_id, str(indice), str(q))
                )
                
        # Extrai e Insere Respostas
        raiz_respostas = (respostas or {}).get("resposta_estruturada", {})
        estrutura_resp = raiz_respostas.get("estrutura_resposta", raiz_respostas) # Fallback compatível
        for indice, lista in estrutura_resp.items():
            for it in (lista or []):
                cursor.execute("""
                    INSERT INTO respostas (bloco_id, indice, quesito, resposta_tecnica, status_tecnico, justificativa_tecnica, observacoes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    bloco_id, str(indice), it.get("quesito", ""), it.get("resposta_tecnica", ""),
                    it.get("status_tecnico", ""), it.get("justificativa_tecnica", ""), it.get("observacoes_adicionais", "")
                ))
                
        conn.commit()

def list_execucoes(termo_busca: str = None) -> list[dict]:
    """Lista as execuções, opcionalmente filtradas pelo nome_processo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, nome_processo, data_criacao FROM execucoes"
        params = []
        if termo_busca:
            query += " WHERE nome_processo LIKE ?"
            params.append(f"%{termo_busca}%")
            
        query += " ORDER BY data_criacao DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_execucao_detalhes(execucao_id: int) -> dict:
    """Retorna um dicionário contendo os detalhes, blocos, provas, quesitos e respostas associadas a uma execução."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Recupera os blocos dessa execução
        cursor.execute("SELECT id, numero_bloco, conteudo_texto FROM blocos WHERE execucao_id = ?", (execucao_id,))
        blocos = [dict(b) for b in cursor.fetchall()]
        
        bloco_ids = [b["id"] for b in blocos]
        
        if not bloco_ids:
            return {"blocos": [], "provas": [], "quesitos": [], "respostas": []}
            
        placeholders = ','.join('?' * len(bloco_ids))
        
        # Provas
        cursor.execute(f"SELECT b.numero_bloco, p.* FROM provas p JOIN blocos b ON p.bloco_id = b.id WHERE p.bloco_id IN ({placeholders})", bloco_ids)
        provas = [dict(r) for r in cursor.fetchall()]
        
        # Quesitos
        cursor.execute(f"SELECT b.numero_bloco, q.* FROM quesitos q JOIN blocos b ON q.bloco_id = b.id WHERE q.bloco_id IN ({placeholders})", bloco_ids)
        quesitos = [dict(r) for r in cursor.fetchall()]
        
        # Respostas
        cursor.execute(f"SELECT b.numero_bloco, r.* FROM respostas r JOIN blocos b ON r.bloco_id = b.id WHERE r.bloco_id IN ({placeholders})", bloco_ids)
        respostas = [dict(r) for r in cursor.fetchall()]
        
        return {
            "blocos": blocos,
            "provas": provas,
            "quesitos": quesitos,
            "respostas": respostas
        }
