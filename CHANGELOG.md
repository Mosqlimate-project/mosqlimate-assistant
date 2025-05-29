Release Notes
---

# 1.0.0 (2025-05-29)


### Bug Fixes

* adicionar valores padrão aos parâmetros da função query_llm ([a536f80](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/a536f80770064d0d498c3dd836c806e96a0f73cf))
* agora testes de faiss_db confirmam a instalação do ollama ([5ecce47](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/5ecce47b309f85be1c107dc51af52e4ec73e56b1))
* ajustar mensagens de prompts e base de validação com valores incorretos ([c9cccea](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/c9cccea73051285958a0781d6af95acc636470cb))
* aplicando pre-commit e corrigindo testes ([9c50c10](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/9c50c103fca280f4eeadf343c1a5985e6eb8f69d))
* assistant examples formatting ([1a4130d](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/1a4130dae10f735e1f6f96d39b02e3100ac3829e))
* bug do pre-commit em que o isort e o black ficavam em loop ([ddae464](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/ddae464c1f26d2dfe3713c95c4f2b03d45f08e71))
* corrige descrição da doença em EpiscannerFilters e ajusta query de exemplo ([0009f96](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/0009f9679151e4c39b245890e02dd0cac7e866ee))
* corrige importação de prompts ([9973304](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/99733045f51fc75b1493ee17dd520891adf99b98))
* erro nos prompts de tabelas com "{" singulares, e reorganização do módulo settings ([7a62e15](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/7a62e159f41d66c8542725a3e276e4ca2185064e))
* **filters:** update structure to simplify reading and update pydantic usage ([4bb7d6e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/4bb7d6edf228ee6572ee6add237c7dfda317eda1))
* **input_validator:** fixed load_asks output to Dict[int, Document] ([699e0ee](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/699e0ee99d4d7ea2cb60e6d22e406e556abae71d))
* **package:** correcting __init__ files and import errors ([b15c40e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/b15c40eee4d4f3355779808826127753a6b59bc7))
* **package:** fixing pre-commit mypy errors in assistant ([655af3e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/655af3e1c510aba727a54fe791aeb6527d28effb))
* **package:** fixing pre-commit mypy errors in utils and input_validator ([13a66ee](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/13a66ee7426f86bb9ee8d496ad8e7cfaa6f21fb2))
* **release:** include workflow_dispatch to dispatch releases ([5a976d0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/5a976d0b77c30dcd3561535e361ad0e86734c392))
* remove 'chik' from enum values in format_api_parameters ([2c39a19](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2c39a19e1bbe7fbf6684d92e05cb6bd89d7c39fa))
* remove importação desnecessária do assistant_ollama ([b15bc30](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/b15bc30a2a406a3f8bf70b1d27f8d1a970335b23))
* remover arquivo de teste desnecessário test_levenshtein.py ([f1b261c](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/f1b261c3daae49a403354a901da12501dba884ef))
* **workflow:** allow release workflow to write contents ([8071ff5](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/8071ff5563ac3d7eb3b5f369e53e50f45aaf26e5))


### Features

* ad new module docs_consumer to get mosqlimate docs ([308e275](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/308e2754c15d22a1c4d86656cadcdfa6c851c45a))
* add compatibilidade com a api do google ([9adbd67](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/9adbd67e35044b88ec9111e62a82738943cbe639))
* add exemplo de pipeline para consulta do assistente ([cc933e2](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/cc933e2df19f47afacf17ef4b13a34826230dc0a))
* add função para formatar parâmetros das tabelas pela api de documentação ([2824c70](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2824c70e29c0d45559eacefa720375ad7de86f73))
* add funções para obter schemas da documentação ([788e1b0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/788e1b0765b638e205e3116b83a280eb1948cd2e))
* add herança de calsse ao assistente, para mais flexibilidade ([324edfd](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/324edfd5479210515b818ed8b46051d2077731b6))
* add logs to analisis of assistant output ([ae32aa4](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/ae32aa400e9d0562c7235b93c6ce67553ab9e287))
* add suporte paralelo ao Ollama e atualiza dependências ([11c80d3](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/11c80d36e9f8ae84e1905a3eedec7ab4a8334d1f))
* adiciona checacgem de relevâcnia e exemplos do banco a query final ([1a2e422](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/1a2e422d270035b75c38951497e2789565ae34fe))
* **api_consumer:** funções de chamadas de api e validação ([c1d096e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/c1d096e742c4e709b5363149964b15479f70c637))
* **configs:** atualizado para uso de pydantic-settings ([fe4994c](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/fe4994c33ccc8834554f17e41951b5aeb059663d))
* **faiss_db:** módulo para gerenciar o banco de dados vetorial ([3f011d6](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/3f011d657a4387a0344d3097eeb82986bc614fd2))
* melhora no rag para obter outputs de perguntas ([3d93399](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/3d9339917c83de9f570f53c409ec7676a9131453))
* **muni_codes:** adicionar funções para processamento e busca de municípios ([616669e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/616669eead9a82cc01d43257dfcd2bcd371612f8))
* **package:** improve repo structure, include linters and semantic-release ([785c588](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/785c588e3372665eec6b08ab2e809c28168d21a1))
* reorganizar importações e atualizar funções para uso de schemas ([2f33e80](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2f33e802a589133967f230c1a7baa554878b6e83))
* **schemas:** adicionar classes de filtros para as tabelas ([4e6b3e4](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/4e6b3e44cd9f27252c7ba2bb1b355edefbc4f7f5))
* **settings:** add settings management with environment variable support ([5d3eed1](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/5d3eed1432ec6c8c3035de37a2aebeb19d49870a))
