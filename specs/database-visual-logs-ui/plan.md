# Plano de Implementação Técnica (plan.md) - Banco de Dados, Logs Visuais e UI Premium

Este plano detalha como as funcionalidades especificadas no [spec.md](file:///e:/Backup_HD_Walter/Cruvinel_dados/Projeto%20Evidencias%20e%20Provas/P4/specs/database-visual-logs-ui/spec.md) serão implementadas no projeto **EVID**.

---

## 1. Arquitetura Proposta

### 1.1 Persistência (SQLite)
*   **Módulo `database.py`**: Conterá todas as conexões SQLite usando o gerenciador de contexto `sqlite3`. A conexão utilizará um arquivo local `evid_provas.db` na raiz do projeto (ou no caminho de execuções).
*   **Inicialização**: O banco será inicializado automaticamente na primeira chamada do aplicativo.
*   **Transacional**: A inserção de cada bloco processado ocorrerá dentro de um bloco transacional (`with conn:`) para assegurar integridade no caso de cancelamento.

### 1.2 Monitoramento Visual (Streamlit)
*   **Contagem de Blocos**: Calculada ao dividir o texto original (`dividir_blocos(texto)`).
*   **Interface em Tempo Real**: Usará o componente `st.progress` e múltiplos containers do tipo `st.empty` para atualizar o progresso de forma síncrona sem encher a tela com novos blocos de logs estáticos.

### 1.3 Design System (WOW UI)
*   **Injeção de CSS**: Cópia do arquivo utilitário `ui_premium.py` da skill localmente no projeto.
*   **Tema (.streamlit/config.toml)**: Definido com cores baseadas no tema dark e cyan vibrante para promover a estética premium.

---

## 2. Detalhamento dos Componentes a Alterar/Criar

### 2.1 Criar `database.py`
Conterá as assinaturas das funções:
```python
def init_db(db_path: str = "evid_provas.db"):
    """Cria as tabelas e índices se não existirem."""

def insert_execucao(nome_processo: str, texto_completo: str) -> int:
    """Registra uma execução e retorna seu ID."""

def insert_bloco_completo(execucao_id: int, numero_bloco: int, conteudo_texto: str, provas: dict, quesitos: dict, respostas: dict):
    """Insere o bloco e todos os dados associados a ele em uma única transação SQLite."""

def list_execucoes(termo_busca: str = None) -> list[dict]:
    """Retorna execuções registradas filtradas pelo termo de busca."""

def get_execucao_detalhes(execucao_id: int) -> dict:
    """Recupera todos os blocos, provas, quesitos e respostas de uma execução específica."""
```

### 2.2 Alterar `main.py`
1.  **Carregar CSS Premium**: Chamar `ui_premium.py -> apply_premium_style()` logo no início de `main.py`.
2.  **Calcular e Registrar Execução**:
    *   No início do lote, inserir a execução e pegar seu `execucao_id`.
3.  **Progresso de Processamento**:
    *   Substituir a área de lote por um painel de monitoramento estruturado com containers `st.empty()`.
    *   Durante a execução de cada bloco, salvar os resultados parciais de Provas, Quesitos e Respostas no banco de dados através da função `insert_bloco_completo()`.

### 2.3 Alterar `historico_interface.py`
*   Substituir a leitura recursiva de arquivos JSON da pasta `execucoes/` por consultas diretas às funções `list_execucoes` e `get_execucao_detalhes` do `database.py`.
*   Inserir campos de filtro (Filtro de busca por termo e filtros visuais de seleção).
*   Reconstruir a lógica do botão de gerar Excel para extrair os dados diretamente do SQLite e exportá-los no formato padrão de 3 abas utilizando o Pandas e OpenPyXL.

### 2.4 Criar `ui_premium.py`
*   Copiar a implementação da skill contendo as funções `apply_premium_style()`, `glass_card()` e `gradient_text()`.

---

## 3. Gestão de Riscos e Casos de Borda

### 3.1 Falhas de Processamento no Meio do Lote
*   **Problema**: A conexão com a API do Gemini pode falhar (timeout ou erro de limites de tokens).
*   **Mitigação**: Os dados dos blocos concluídos já estarão salvos no SQLite (visto que inserimos a cada bloco concluído). O usuário poderá reprocessar a mesma execução sem perder o que já foi computado, reaproveitando os blocos salvos (baseado no `numero_bloco` e `execucao_id`).

### 3.2 Concorrência de Leitura/Escrita no SQLite
*   **Problema**: O SQLite pode travar se houver múltiplas conexões de escrita simultâneas (`database is locked`).
*   **Mitigação**: Como a aplicação roda localmente e o processamento é síncrono (um bloco por vez no loop principal), o risco de concorrência de escrita é mínimo. Para garantir, usaremos timeouts adequados na conexão SQLite (`sqlite3.connect(..., timeout=30)`).
