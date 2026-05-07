# Mosqlimate Assistant

Assistente RAG para a plataforma Mosqlimate com arquitetura de agente único, ferramentas por bloco documental e índice vetorial FAISS via LangChain.

## Visão geral

O fluxo principal agora é simples:

1. o usuário faz uma pergunta
2. o agente escolhe uma ou mais ferramentas temáticas
3. cada ferramenta recupera trechos do bloco documental correspondente
4. o agente compõe a resposta final com base apenas nesses trechos

Blocos padrão:

- `platform_overview`: visão geral mais completa do projeto, produtos, OviCounter, autenticação e acesso inicial
- `platform_epi_data` e `platform_env_data`: blocos do datastore ampliados com mais contexto epidemiológico, climático e vetorial
- `platform_registry_models` e `platform_registry_predictions`: registry com mais contexto de modelos e previsões por fluxo
- `platform_visualize`: dashboards, métricas e interpretação das previsões
- `mosqlient_getting_started`, `mosqlient_datastore`, `mosqlient_registry`, `mosqlient_scoring_tutorial`, `mosqlient_score_reference`, `mosqlient_forecast_baseline`, `mosqlient_ensemble` e `mosqlient_prediction_optimize`: blocos do cliente com mais documentação agregada por fluxo
- `imdc_overview` e `imdc_data`: visão geral, dados, instruções, cronograma e contexto de resultados do sprint/IMDC atual

## Organização dos módulos

O pacote foi estruturado para separar claramente cada responsabilidade:

- `mosqlimate_assistant/__init__.py`: interface pública do pacote, com os símbolos principais reexportados.
- `mosqlimate_assistant/main.py`: ponto de montagem do runtime padrão e wrappers convenientes para uso externo.
- `mosqlimate_assistant/assistant.py`: wrapper de alto nível do runtime, responsável por configurar o agente e expor `query()`.
- `mosqlimate_assistant/agent.py`: loop principal de tool-calling com LangChain, seleção de ferramentas e resposta final.
- `mosqlimate_assistant/knowledge_base.py`: catálogo de blocos documentais, transformação em documentos LangChain e índice FAISS.
- `mosqlimate_assistant/document_consumer.py`: ingestão, normalização, resolução de includes e chunking da documentação.
- `mosqlimate_assistant/embeddings.py`: provedores de embedding usados pela camada de recuperação.
- `mosqlimate_assistant/models.py`: modelos Pydantic compartilhados pelo pacote.
- `mosqlimate_assistant/prompts.py`: prompts de sistema usados pelo agente.
- `mosqlimate_assistant/monitoring.py`: logs estruturados, extração de uso e cálculo/normalização de custo.
- `mosqlimate_assistant/settings.py`: configuração simples do pacote baseada em variáveis de ambiente.

## Instalação

```bash
uv sync
```

## Uso rápido

```python
from mosqlimate_assistant.main import assistant_pipeline

answer = assistant_pipeline(
    question="Como obter uma API key e consultar dados do Infodengue?",
    google_api_key="<YOUR_DEEPSEEK_API_KEY>",
    lang="pt",
)

print(answer)
```

Também é possível omitir o parâmetro e configurar a credencial via variável de ambiente:

```bash
export DEEPSEEK_API_KEY="<YOUR_DEEPSEEK_API_KEY>"
```

## Desenvolvimento

```bash
uv run pytest
```

Os testes estão organizados por responsabilidade (`runtime`, `catalog/data`, `agent`, `pipeline`, `monitoring`, `models`, `settings`), seguindo a mesma separação conceitual dos módulos do pacote.
