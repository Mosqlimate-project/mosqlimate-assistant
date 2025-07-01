Release Notes
---

# [1.5.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.4.2...1.5.0) (2025-07-01)


### Bug Fixes

* **data:** remove old databases data and update lock file ([ad0de17](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/ad0de17484a838f4c33be33fc43afc7744b35315))
* **dependencies:** remove unused dependencies and update __init__.py ([f24a3b0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/f24a3b0461b9295da88b8c7a9cb2474d5082c63a))
* **old_databases:** remove old databases, chroma_db.py and faiss_db.py ([24add90](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/24add90cc784397c9a5e9aebaf22ae7b81840a36))
* **tests:** reorganize test imports and remove unused test_faiss_db.py ([7852fc9](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/7852fc988e9ed56bb6a2c9836da67b2f1c2e523e))


### Features

* **vector_db:** implement VectorDB using pandas, numpy and pickle files ([8b20529](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/8b20529e01b8bab5118484bab07ec414c5480143))

## [1.4.2](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.4.1...1.4.2) (2025-06-30)


### Bug Fixes

* **docs:** update markdown URL's to the correct link, and add tests for docs consumer ([a7976a0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/a7976a02140008605eaf5ad84f73c81d52c6ad78))

## [1.4.1](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.4.0...1.4.1) (2025-06-27)


### Bug Fixes

* **docs:** update markdown documentation URLs ([c72eeb2](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/c72eeb23e154fa322648ed492e5fc67857efde15))
* **pyproject:** add chromadb to dependencies and add chroma db data ([3105552](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/310555260d174577e907c94c4cbafbe0ba8dbb60))

# [1.4.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.3.0...1.4.0) (2025-06-26)


### Bug Fixes

* **pyproject:** remove langchain-ollama and add numpy to dependencies, update manifest ([84c113d](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/84c113dfb9373610fa2cb3298d92b01c5cc69ac4))


### Features

* **embedding:** implement OllamaEmbeddingWrapper for document and query embedding ([e449cb7](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/e449cb785ce8b82bad80bc0b269c0e3d50b1ff44))

# [1.3.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.2.3...1.3.0) (2025-06-25)


### Features

* **embedding:** add support for custom Ollama URL ([690560a](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/690560a55c831b2c5d6d1ab44784037cb9be2ad4))

## [1.2.3](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.2.2...1.2.3) (2025-06-25)


### Bug Fixes

* **data:** move fixed data "../" to project relative path "./" ([80022fa](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/80022fa297c07a2192ab417ac07f3fa9690ddade))
* **settings:** add func to ensure local files exist by downloading from github ([906157f](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/906157fba9155ab339a5712fb911edf55cc7c455))

## [1.2.2](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.2.1...1.2.2) (2025-06-25)


### Bug Fixes

* **pyptoject:** add MANIFEST.in to include data in package ([7189215](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/71892159e79e88bd6d979e7f404d0c70c6c2b4c8))

## [1.2.1](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.2.0...1.2.1) (2025-06-25)


### Bug Fixes

* **pyproject:** add package data inclusion and specify files for poetry ([053f521](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/053f521eb8f0f89ff1458b918964007c3e8bce08))

# [1.2.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.1.0...1.2.0) (2025-06-23)


### Bug Fixes

* **docs:** add markdown link to the docs as a comment ([317d1b3](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/317d1b334b4c799bea2ee947bcdb90807db4f48e))
* **faiss_db:** move get_relevant_sample_asks from assistant to faiss_db module ([337f707](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/337f70792c0996b038ee2771fe58a8b7868497f0))
* **faiss_db:** update asks_db to corrected asks ([7e370e0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/7e370e0ec7ab6326d0d360be8af445ac05d3d858))
* **settings:** adding more mosqlimate documentation links ([c2c4902](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/c2c4902accaa9891dd5e7bbd8c35cd3abf9f41e3))


### Features

* **assistant:** add new methods for assistant to handle with mosqlimate documentation ([5223c52](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/5223c522bdb05cad3a0c358ffe681ea96ca2ad38))
* **docs:** add funcs to load or save mosqlimate docs on FAISS vector store ([720f999](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/720f9995def6f26a817e674eb599af061f7e20af))
* **docs:** add functions to get mosqlimate markdown documentation ([33f8eac](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/33f8eac9c75c3f549e39edd66829047829436a79))
* **docs:** add mosqlimate docs keyword mapping ([84d992e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/84d992e2eeea2f13b8c937254c723fd5a5dd7636))
* **examples:** add example of new pipeline usage ([f5b5528](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/f5b55281659d885cb824fe2d94f3c7d997979ab5))
* **main:** add pipeline for consulting api, and documentation ([2e5c882](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2e5c882bca85fc319056aaac3a59305a162a0343))

# [1.1.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.0.1...1.1.0) (2025-06-03)


### Bug Fixes

* linting modules ([1f34b38](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/1f34b38392640b0c757578ba16224aa3d12e59c3))
* **schemas:** Default date handling to lase epiweek ([19dfed8](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/19dfed85e888d2cc01ee6d972f70c5996c39a704))


### Features

* added epiweek dependency to the project ([6063660](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/6063660d4c89d8fa4e6776bc469424ebf679377b))
* now using last epiweek if start or end date are invalid or not provided ([6ba3b2c](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/6ba3b2c098c76be7cd100454805c992491a30523))

## [1.0.1](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.0.0...1.0.1) (2025-05-29)


### Bug Fixes

* **release:** include missing prompts on release ([5fc81e4](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/5fc81e4f749344b20ae0a90c6226e5c11f2240bc))

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
