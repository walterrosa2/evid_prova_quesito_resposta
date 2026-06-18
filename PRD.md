# PRD - Projeto EVID (Melhorias de Banco de Dados, Logs Visuais e Interface Premium)

## 1. Objetivo do Projeto
Melhorar a aplicação **EVID - Provas e Quesitos** com o objetivo de:
1.  **Persistir** os dados das análises em um banco de dados local SQLite, prevenindo perda de informações e possibilitando consultas históricas e re-exportação para planilhas Excel.
2.  **Melhorar a experiência do usuário (UX)** através de feedback de processamento síncrono e progressivo (log visual) em tempo real, informando o número total de blocos a serem processados.
3.  **Refinar a interface (UI)** de acordo com os padrões visuais premium ("WOW UI") propostos no projeto, utilizando componentes customizados, efeitos modernos de glassmorphism e tipografia limpa.

---

## 2. Usuários da Aplicação
*   **Peritos Judiciais e Assistentes Técnicos**: Usuários que analisam grandes processos jurídicos para mapear evidências, formular quesitos periciais e simular respostas. Eles necessitam de alta confiabilidade nos dados históricos e de relatórios perfeitamente organizados para exportação.

---

## 3. Requisitos e Escopo

### Requisitos de Interface e Experiência do Usuário (UI/UX)
*   **UI Premium ("WOW UI")**: Incorporação dos estilos contidos em `ui_premium.py` da skill `streamlit-wow-ui` (fontes Inter/Outfit, cores baseadas em HSL/Dark, cards no estilo Glassmorphism, textos com gradiente).
*   **Painel Visual de Processamento**: Exibição da volumetria calculada de blocos antes da execução. Acompanhamento etapa por etapa de forma dinâmica com o componente `st.progress` e logs legíveis em tela.

### Requisitos de Persistência e Histórico
*   **Banco de Dados Local (SQLite)**: Inicialização automática de um arquivo SQLite (`evid_provas.db`) para persistência de execuções históricas.
*   **Tabelas**: Estrutura contendo tabelas de `execucoes`, `blocos`, `provas`, `quesitos` e `respostas`.
*   **Tela de Histórico de Execuções**: Permitir ao usuário visualizar e filtrar as execuções antigas do banco de dados na própria tela do Streamlit.
*   **Exportação Histórica**: Permitir exportar qualquer consulta de execução antiga direto para Excel (`.xlsx`) no mesmo layout de 3 abas ("Provas", "Quesitos" e "Respostas").

---

## 4. Limitações e Premissas
*   **Independência de Ambiente**: O banco SQLite deve residir localmente e persistir os dados no diretório de dados da aplicação (`execucoes/` ou raiz do projeto).
*   **Sem Conflitos com o Fluxo JSON**: Os arquivos JSON locais de processamento intermediário serão mantidos para manter compatibilidade e auditoria física, mas o banco de dados será a fonte principal para a interface de histórico e re-exportação.
*   **Instalações Locais**: A biblioteca do banco SQLite (`sqlite3`) já faz parte do core do Python. Bibliotecas adicionais não serão estritamente necessárias além do pandas e openpyxl que já estão no projeto.

---

## 5. Dados Sensíveis / PII (Informações de Identificação Pessoal)
*   Como a ferramenta lida com processos judiciais reais carregados pelo usuário Walter, os dados podem conter nomes de partes, CPFs, e outras informações sensíveis.
*   **Segurança Física**: O banco de dados SQLite é mantido localmente na máquina do usuário Walter e não deve ser compartilhado nem exposto a conexões de rede públicas.
*   **Higiene de Logs**: Os logs de depuração do sistema não devem armazenar o conteúdo sensível completo dos blocos nos terminais de forma não segura; os textos detalhados devem residir somente nos arquivos estruturados autorizados.
