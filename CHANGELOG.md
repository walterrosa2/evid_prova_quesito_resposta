# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased / v1.1.0] - 2026-06-18
### Added
- Persistência das análises usando SQLite local nativo (`database.py`), mantendo um histórico inquebrável de execuções de blocos, provas, quesitos e respostas.
- Componente visual síncrono no Streamlit na aba de Nova Análise que informa previamente a volumetria de processamento e a atualiza no progresso (`main.py`).
- Módulo `ui_premium.py` incorporando elementos de Glassmorphism, fontes refinadas e CSS dark-mode.
- Filtro de buscas de execuções históricas por termo diretamente no SQL (em `historico_interface.py`).
- Botão "Ver Tabelas Detalhadas" que expõe sub-dataframes para provas, quesitos e respostas de execuções históricas.
- Botão nativo de re-exportar relatórios consolidados em Excel `.xlsx` na interface de histórico.

### Changed
- Refatorada a função global de análise `executar_todas_as_etapas` para não apenas gerar JSONs locais, mas processar via transações os inserts do banco de dados (SQLite).
- Substituição da lógica de listagem do painel de histórico de execuções: saiu a busca recursiva de pastas em arquivos físicos e entrou a filtragem via banco de dados relacional.
- Melhoria visual de todos os cabeçalhos das telas Streamlit, passando a adotar as cores gradientes `#00D1FF` e estilização premium.
