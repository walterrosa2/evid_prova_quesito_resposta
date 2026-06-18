# Especificação da Feature: Banco de Dados de Resultados, Logs Visuais e Interface Premium

## 1. Visão Geral
Esta especificação define o comportamento e as melhorias a serem implementadas no sistema **EVID - Provas e Quesitos**. O objetivo é melhorar a experiência de uso através de uma interface de usuário refinada, aumentar a transparência sobre o andamento do processamento em lote e fornecer um repositório histórico persistente e consultável para análises passadas, permitindo sua recuperação e exportação.

---

## 2. Atores e Papéis
*   **Analista Técnico / Perito (Usuário Principal)**: Deseja carregar textos jurídicos/periciais, acompanhar o processamento de forma transparente, realizar consultas a análises feitas anteriormente, aplicar filtros sobre os resultados e baixar relatórios estruturados para utilização em suas peças processuais.

---

## 3. Cenários de Usuário (User Scenarios)

### Cenário 1: Visualização do Progresso em Tempo Real
**Dado** que o usuário carregou um documento longo e iniciou o processamento em lote,
**Quando** o processamento começar,
**Então** o sistema deve informar previamente a quantidade total de blocos gerados e exibir um log visual contínuo e interativo mostrando o progresso detalhado de cada subetapa (Mapeamento de Provas, Geração de Quesitos e Simulação de Respostas) para cada bloco, permitindo que o usuário saiba exatamente o que está acontecendo e quanto tempo falta.

### Cenário 2: Consulta e Filtragem de Análises Anteriores
**Dado** que o usuário já realizou diversas análises no passado,
**Quando** ele acessar a tela de consulta de histórico,
**Então** ele deve conseguir filtrar as análises por nome do processo, data da execução ou termos específicos nos resultados, visualizar os detalhes de uma análise selecionada diretamente na tela e trabalhar nos resultados obtidos.

### Cenário 3: Re-exportação de Relatórios do Histórico
**Dado** que o usuário localizou uma análise antiga no histórico através dos filtros,
**Quando** ele clicar na opção de exportação,
**Então** o sistema deve gerar e disponibilizar o download do relatório em formato de planilha (Excel) contendo exatamente os dados daquela execução histórica estruturada de forma idêntica à exportação da análise em tempo real.

---

## 4. Requisitos Funcionais

### RF-01: Persistência Durável de Resultados
*   O sistema deve armazenar de forma persistente todos os resultados de análises gerados (metadados da execução, blocos de texto, provas mapeadas, quesitos gerados e respostas simuladas).
*   A persistência deve ser local e independente dos arquivos JSON temporários gerados durante o processamento.

### RF-02: Monitoramento e Log de Processamento em Tempo Real
*   Antes do início da execução em lote, o sistema deve calcular e exibir a volumetria total (quantidade de blocos e subetapas necessárias).
*   A interface deve mostrar um indicador de progresso global e mensagens de log detalhadas à medida que cada bloco conclui uma subetapa.
*   Mensagens de progresso não devem sobrecarregar a tela, mantendo uma visualização limpa e estruturada.

### RF-03: Consulta e Trabalho sobre Execuções Anteriores
*   Deve existir uma interface dedicada para visualização de análises históricas.
*   O usuário deve poder pesquisar execuções por palavra-chave (ex: Nome do Processo) e filtrar por intervalo de datas.
*   Ao selecionar uma execução, o usuário deve conseguir visualizar os resultados detalhados estruturados (provas, quesitos e respostas) em formato de tabelas interativas na tela.

### RF-04: Exportação de Histórico para Planilhas
*   A partir de qualquer execução selecionada no histórico, o usuário deve poder exportar um arquivo XLSX estruturado com as mesmas três abas (Provas, Quesitos, Respostas) geradas no fluxo principal.

### RF-05: Design e Estética Premium
*   A interface da aplicação (sidebar, botões, cards e textos) deve seguir uma identidade visual consistente com paletas de cores modernas, tipografia otimizada e elementos com feedback visual fluido.

---

## 5. Critérios de Sucesso (Mensuráveis)
1.  **Tempo de recuperação histórica**: Um usuário deve conseguir localizar e abrir qualquer execução realizada no passado em menos de 3 segundos utilizando os filtros de busca.
2.  **Transparência de execução**: 100% dos blocos e etapas processados durante uma análise devem ter seu progresso refletido visualmente em tempo real na tela do usuário.
3.  **Fidelidade dos dados históricos**: Relatórios gerados a partir do histórico devem ser semanticamente idênticos aos relatórios gerados imediatamente após a execução da análise correspondente.
4.  **Consistência de Design**: Toda a interface deve herdar o tema e os estilos visuais premium sem quebras de layout ou fontes padrão do navegador.

---

## 6. Entidades de Dados (Esquema Conceitual)

### 6.1 Execução (`execucoes`)
*   `id` (Identificador único)
*   `nome_processo` (Texto)
*   `data_criacao` (Data/Hora)
*   `texto_completo` (Texto contendo o documento original integrado)

### 6.2 Bloco (`blocos`)
*   `id` (Identificador único)
*   `execucao_id` (Chave estrangeira relacionando à Execução)
*   `numero_bloco` (Inteiro, ex: 1, 2, 3...)
*   `conteudo_texto` (Texto do bloco)

### 6.3 Prova Mapeada (`provas`)
*   `id` (Identificador único)
*   `bloco_id` (Chave estrangeira relacionando ao Bloco)
*   `indice` (Texto/Código de identificação da prova no bloco)
*   `tipo` (Texto, ex: Documental, Testemunhal)
*   `resumo` (Texto)
*   `referencia` (Texto)
*   `conteudo` (Texto)

### 6.4 Quesito Gerado (`quesitos`)
*   `id` (Identificador único)
*   `bloco_id` (Chave estrangeira relacionando ao Bloco)
*   `indice` (Texto/Código de identificação do quesito no bloco)
*   `quesito` (Texto contendo a pergunta gerada)

### 6.5 Resposta Simulada (`respostas`)
*   `id` (Identificador único)
*   `bloco_id` (Chave estrangeira relacionando ao Bloco)
*   `indice` (Texto/Código de identificação da resposta no bloco)
*   `quesito` (Texto contendo o quesito correspondente)
*   `resposta_tecnica` (Texto contendo a resposta gerada)
*   `status_tecnico` (Texto, ex: Conclusivo, Inconclusivo)
*   `justificativa_tecnica` (Texto)
*   `observacoes` (Texto)

---

## 7. Assunções e Limitações
*   **Assunção**: A estrutura do banco de dados local deve ser inicializada de forma transparente na primeira inicialização da aplicação, sem exigir scripts de migração manuais do usuário.
*   **Limitação**: A exportação para Excel depende de as tabelas de banco de dados conterem registros correspondentes à execução em si; execuções corrompidas ou parciais não armazenadas podem não possuir abas completas.
