# EVID – Alterações estruturais (Remoção Etapa 1 + Prompts por etapa + Excel 3 abas)

## O que foi alterado
1) **Remoção completa da Etapa 1 (Índices) do `main.py`**
   - UI e fluxo agora exibem apenas **Etapas 2, 3 e 4** (Provas → Quesitos → Respostas).
   - Nenhuma checagem de “cobertura de índices” é feita.
   - A Etapa 2 não busca mais índices; mapeia evidências diretamente do texto (grupo único `'GERAL'` quando não houver índices).

2) **Prompts dedicados por etapa no `prompt_engine.py`**
   - `run_prompt(etapa, funcao, texto, prompt_name=None)`
   - Procura os arquivos na seguinte ordem:
     - `prompts/{prompt_name}.txt` (se informado)
     - `prompts/Prompt_V1 2406_old2.txt`
     - `prompts/Prompt_V1 2406.txt`
     - `./Prompt_V1 2406_old2.txt` (fallback legado)
   - Os módulos agora chamam:
     - Etapa 2: `prompt_etapa_evidencias`
     - Etapa 3: `prompt_etapa_quesitos`
     - Etapa 4: `prompt_etapa_respostas`

3) **Módulos ajustados para operar sem índices**
   - `evidence_mapper.mapear_provas(...)` → aceita `indices` opcional; quando ausente, consolida sob `'GERAL'`.
   - `quesito_generator.gerar_quesitos(...)` → idem; se não houver índices, retorna `'GERAL'` com lista de strings.
   - `resposta_simulator.simular_respostas(...)` → sem mudança de dependência; usa os prompts específicos.

4) **Aggregator tolerante a `'GERAL'`**
   - `aggregator.carregar_resultados(...)` agrupa blocos por tipo (`provas/quesitos/respostas`) aceitando chaves `'GERAL'` ou índices legados.
   - `gerar_estrutura_final(...)` monta `estrutura['blocos'][].indices[]` com `indice`, `provas`, `quesitos`, `respostas`.

5) **Excel final com 3 abas no `report_generator.py`**
   - “Etapa Evidencias”: `tipo, conteúdo, resumo, referencia`
   - “Etapa Quesitos”: `Quesitos`
   - “Etapa Respostas”: `quesito, resposta, status tecnico, justificativa, observações`
   - Mecanismo de pareamento de `quesito` ↔ `resposta`: se o campo `quesito` não vier no JSON de respostas e o número de respostas = número de quesitos, o texto do quesito é atribuído por posição.

6) **Histórico corrigido (`historico_interface.py`)**
   - Remove referência a `relatorio['indices']` e exibe contagens agregadas por blocos, grupos, evidências, quesitos e respostas.

## O que você precisa fazer
1) **Criar os novos prompts** (na pasta `prompts/` do projeto):
   - `prompt_etapa_evidencias.txt`
   - `prompt_etapa_quesitos.txt`
   - `prompt_etapa_respostas.txt`
   > Enquanto você não criar esses arquivos, o sistema usa fallback para `Prompt_V1 2406_old2.txt`.

2) **(Opcional) Remover arquivos e imports legados** relacionados à Etapa 1
   - `index_identifier.py`, `indices_runner.py`, `merge_indices.py` podem permanecer no repo, mas `main.py` não os utiliza.

3) **Configurar variável de ambiente (recomendado)**
   - Mova a `GOOGLE_API_KEY` do `config.py` para variável de ambiente e ajuste o `config.py` para ler via `os.getenv` (se desejar).

## Arquivos atualizados neste pacote
- main.py
- prompt_engine.py
- evidence_mapper.py
- quesito_generator.py
- resposta_simulator.py
- aggregator.py
- report_generator.py
- historico_interface.py