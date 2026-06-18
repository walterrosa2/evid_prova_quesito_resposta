import database

def testar_fluxo_db():
    print("Iniciando banco de dados...")
    database.init_db()
    print("Banco inicializado com sucesso.")

    print("Inserindo execução de teste...")
    exec_id = database.insert_execucao("Processo de Teste Validação", "Texto base do processo completo.")
    print(f"Execução inserida com ID: {exec_id}")

    print("Inserindo bloco de teste...")
    provas_mock = {"resposta_estruturada": {"idx1": [{"tipo": "Documental", "resumo": "Teste", "referencia": "Pag 1", "conteudo": "Doc 1"}]}}
    quesitos_mock = {"resposta_estruturada": {"idx1": ["O que é isso?"]}}
    respostas_mock = {"resposta_estruturada": {"estrutura_resposta": {"idx1": [{"quesito": "O que é isso?", "resposta_tecnica": "É um teste", "status_tecnico": "Conclusivo"}]}}}

    database.insert_bloco_completo(exec_id, 1, "Conteudo bloco 1", provas_mock, quesitos_mock, respostas_mock)
    print("Bloco inserido com sucesso.")

    print("Consultando execuções...")
    lista = database.list_execucoes("Teste")
    print(f"Encontradas {len(lista)} execuções com a palavra 'Teste'.")

    print("Testando detalhes da execução...")
    detalhes = database.get_execucao_detalhes(exec_id)
    print(f"Detalhes retornados: Blocos ({len(detalhes['blocos'])}), Provas ({len(detalhes['provas'])})")

if __name__ == "__main__":
    testar_fluxo_db()
