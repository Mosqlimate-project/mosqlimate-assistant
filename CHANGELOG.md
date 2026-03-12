Release Notes
---

# [1.8.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.7.2...1.8.0) (2026-03-12)


### Bug Fixes

* **assistant:** improve error management and correct type hints ([2cbba2d](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2cbba2dae62d5b5b0c788f96396d9ce8a07a2a55))
* **document_consumer:** enhance content processing and error handling ([0920ee6](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/0920ee62aa9b2e113df2759e5914734bd21791fb))
* **examples:** remove decrepated example notebooks ([f4be735](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/f4be735957ff974694a52d6d0146302396bedede))
* **modules:** update dependencies and package structure for v2.0.0 release ([04c567e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/04c567eccffe30793cbec96a76d931265b017b1d))
* **prompts:** update coder agent prompt to improve usability ([e235d20](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/e235d206108939a8f0ca123c90cd209e4059b18a))
* **release:** adjust formatting and add Python package build step ([34536d7](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/34536d760f9517c52896b1073a6cacab4aeddaa1))
* **semantic_release:** fixing problens ([ba442ee](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/ba442eeb0c46af6680316c4d04cb86725c16b6be))
* **semantic_release:** fixing problens ([0b86b90](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/0b86b90b77a955d680debde6e6ee40880aca1617))
* **settings:** streamline settings and remove unused variables ([6675081](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/66750814f726177d2e11ea041ea9aad86e43facf))
* **tests:** reorganize imports and linting in test files ([314cb80](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/314cb806c96a7e7488af5569174d3dc136b99edf))
* **vector_store:** remove obsolete vector store file ([f03fc0c](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/f03fc0cb8a51edf9c15ad323311ab01a2eb802b7))
* **workflow:** update Node.js version to 22.14.0 ([ed4e088](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/ed4e08880fd064ac20acdda0abf7991da1edc903))


### Features

* **.gitignore:** add http_cache and ruff_cache to ignore list ([533ca5c](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/533ca5c499b9a86874e1487bcbea8e0daaa947d1))
* **agent_cards:** add agent cards to future code refactor ([e10d1be](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/e10d1be3c4475490072028732ef670cbb14116fe))
* **agent_cards:** refactor AgentCard class to improve prompt handling ([cad20bc](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/cad20bc34639e5a41abb2787310bbd751280a498))
* **agent:** add fallback mechanism and improve schema methods ([2c62ac7](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2c62ac79fe258d69f9da3bf4a571e38a98a3e059))
* **agent:** add support for custom named groups search ([eb60d52](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/eb60d52e8298bfbc99506c139541c9ea1f175c54))
* **agents:** implement classes for agent management and execution ([2ca3541](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2ca35412f6c19e9335d25b8511fecd4a11f32d52))
* **assistant:** refactor Assistant and add support for multiple assistant ([3ccaf2f](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/3ccaf2f41ea608d7445c7675fb4e3df6816c27a8))
* **cache:** implement shared cache session for HTTP requests ([8400d9e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/8400d9e30fc96ecbcc580084e595983b475f0c72))
* **code_refs:** add csv with code references ([a532f9b](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/a532f9b60ee0b070a53b5b2ebba3763f13ef6514))
* **coder:** add funcs for mosqlient code docs ([a6c578a](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/a6c578a1b0409dfb2116fd7b96627bb03979c1d2))
* **coder:** add functions to build coder agent prompts ([b671fb8](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/b671fb83b841a05431ee81f0f1731b732a40b47f))
* **coder:** integrate coder agent functionality to assistant ([fa42530](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/fa4253036adbefe1171d95f46cad1bb38d254987))
* **consumer:** implement document fetching consumers ([2b664d5](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/2b664d53a749aa6b46f7408fda057c55f1d4844c))
* **data:** add new CSV files for code, docs, and IMDC ([4fc5d20](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/4fc5d200cae5411fe503f32a1a5585b421f40f5a))
* **embeddings:** implement base and provider classes for embedding queries ([efc8024](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/efc80249e6e82bf3ae6050c88e69684667d7537e))
* **models:** add data models for providers and document ([3c823a4](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/3c823a4320dcbe280ce3230bf983b26533d5c47e))
* **prompts:** add new prompts for docs, coder, and IMDC agent ([55d050e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/55d050ef2b8464dbb660dff574b2387e89587206))
* **providers:** implement multiple provider classes for llm ([82b9040](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/82b9040c55d46763da690c0b4f54be8d6fe422db))
* **providers:** update provider types and refactor provider classes ([18855ae](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/18855aed3aef417c8d1788a5b2df32dd25b7696d))
* **tests:** add tests for models.py ([5fbb255](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/5fbb255a35cc553b544453447ec9ba1aafb9c824))
* **tests:** add tests for prompt generation functions ([13a2478](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/13a24784c3887a505647d7c7149b453df5e125b4))
* **tests:** add tests for vector store ([406ce1f](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/406ce1f154771c589bd00d2f433f78813a8d5f3f))
* **tests:** add unit tests for agent cards and tools ([29fdb8f](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/29fdb8f73e3cc3a90d0917b9d5a3c20267095dff))
* **tests:** add unit tests for embeddings ([1f87ed7](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/1f87ed7232dfc1ea755c5e9d08e1ad024415d924))
* **tests:** add unit tests for settings ([002d9c7](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/002d9c78152bb98dfb7a16d8c8cdd65d0f855677))
* **vector_store:** implement group search for custom groups ([bf370e0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/bf370e084b8468639c6bbcd0002dac3b6c78ce77))
* **vector_store:** simplify embedding logic and clean up comments ([67b2ee2](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/67b2ee263d9700f451bfa1b1c4f2d4782d6503f1))

## [1.7.2](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.7.1...1.7.2) (2025-09-24)


### Bug Fixes

* **func_tools:** Simplify code examples for clarity ([94d8763](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/94d87630b84d6057033396f633766fa0f3f34758))

## [1.7.1](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.7.0...1.7.1) (2025-09-18)


### Bug Fixes

* **pipeline:** adjust pipeline to handle message history ([bf931d8](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/bf931d8e9b1c11717452b4f11fad267cf3d6346b))

# [1.7.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.6.0...1.7.0) (2025-09-18)


### Bug Fixes

* **assistant:** add optional x_uid parameter to handle_tool_calls and related functions ([a322aa3](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/a322aa30a875ffeab6c0d365bfccfddec40a4043))
* **assistant:** add support for assistant messages in message history ([c1bced4](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/c1bced44feb024b79f213ae07f033be8a587d36c))
* **assistant:** minor fixes in prompt and model return structure ([682a0fa](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/682a0fa5c2e7cfd55a718c6be478dad44f5dab9c))
* **assistant:** update similar_docs parameter to be optional ([08b72bd](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/08b72bd0840cb4cc481d7102eeaf44fc502f8850))
* **blocks:** update documentation blocks for similar queries ([d89927d](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/d89927d3b776de95d4f442a01bf6f410bf315c3a))
* **dependencies:** update dependencies and vector store ([adc4c1e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/adc4c1e57506d44539d7a8b305df2390d1bf0e22))
* **func_tools:** improve return structure and add reference links ([91175d1](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/91175d14479446d73ad5fba6cd01e2228c9cdf80))
* **pipeline:** make similar_docs parameter optional and improve handling ([163bfae](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/163bfae1e1418dbb563163f673653c91addab90b))
* **prompts:** now using DEFAULT_DOCS_LIST as all documentation source ([aee550c](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/aee550cae888a5cc07b5e4e7966b721110cbea01))
* **prompts:** remove example questions and improve instructions ([4328f55](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/4328f55d5ae237a8676b57a1564eb6703df58a98))
* **prompts:** remove unused functions ([99e45a0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/99e45a01e9c795e7e53edd000ce8ac30a87d5840))
* **tests:** update success message assertions ([8df9942](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/8df99420d70c4e63622f8b71928d34e84cd3243d))


### Features

* **assistant:** enhance message handling and add message_history support ([e502cb0](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/e502cb00bd25000b3f6be2751e817bdfc5be8efd))
* **assistant:** improve code execution and prompt clarity ([b1ff878](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/b1ff8780ceb278377e9635e41653703e4f6b2eb1))
* **vector_db:** replace use_keywords with embedding_column for document processing ([459a7f3](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/459a7f318f44df31eacf07eb7efa019e7a585d9c))
* **vector_db:** update document serialization to use pickle for vector store ([c2ab130](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/c2ab130ace216a7e6c8dc9032abe26aab86588b5))

# [1.6.0](https://github.com/Mosqlimate-project/mosqlimate-assistant/compare/1.5.0...1.6.0) (2025-09-05)


### Bug Fixes

* **api:** remove deprecated API consumer and schema definitions ([1a5b0f7](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/1a5b0f711df7a691fb6afc7f152822582430a1a2))
* **assistant:** cast tool schemas to correct type, remove unused test imports ([b803835](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/b8038355aaa1f44188f42b65a9b380c7db1945cb))
* **codebase:** update type hints in vector_db and muni_codes ([eb4f0ae](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/eb4f0ae28d2b5526a2d88dd726843fe995d58f3f))
* **docs:** add docs links for various endpoints ([13cd15d](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/13cd15de499efae56940b03e8f86b27f0454e2c3))
* **docs:** update load_docs_documents to use full markdown content and improve metadata ([9d3a923](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/9d3a923212f38c7e2437765be40185a8de2679c8))
* **main:** remove unused API pipeline and related imports ([4f34a86](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/4f34a862ee08182b6c8f5cd0cc162c44fec60249))
* **muni_codes:** streamline input processing and improve closest match logic ([f2a517e](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/f2a517ea62c3053d767aa487f16efd4eca9708bc))
* **settings:** update GEMINI_MODEL version to 2.5-flash ([d63d2ab](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/d63d2ab9b17a80e85768544d2248e1ec8517e631))
* **tests:** remove obsolete test files for API consumer and schemas ([9df44ae](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/9df44ae1962aa6de6746085873fa860d9c29c61c))
* **tests:** remove unused imports and update tests ([7f2c8d1](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/7f2c8d1cb0358425213d6ae9d0f5f7a4e5237ecb))
* **utils:** simplify JSON answer formatting ([173ccab](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/173ccab3ce8b032aede9b27542926a61d186c3cb))


### Features

* **assistant:** implement tool calling functionality and enhance prompt instructions ([e71abc3](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/e71abc387b612fda2bdfa79c48fe0dba0149a0e2))
* **data:** add keywords_map.csv with mosqlimate docs links and keywords ([822b1be](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/822b1be608894d847463af8eb8e5241301448653))
* **docs:** add DOCS_BLOCKS_MAP for improved documentation organization ([52d0e53](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/52d0e5359d53ee3f1483cd301ab4a905efcba014))
* **docs:** implement functions to use  document blocks, concatenating documents ([1375908](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/1375908048286b3b3d488390da8f3b15cbefa7e1))
* **docs:** remove deprecated documentation URLs and implement dynamic content retrieval ([d0d5aae](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/d0d5aae09d139c9a15fd1f0c6cad8d2330c7cf97))
* **func_tools:** add func tools for assistanto to do api calls ([a8edc17](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/a8edc1727f10ffe7f61d6f939cab8fc419121fee))
* **prompts:** update base prompts to improve performance ([3ad9181](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/3ad91818c243a26cb2b19e42ccf8427b9647c7a2))
* **tests:** add func_tools tests ([9f7a4d4](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/9f7a4d4f0e960c4ddfe7879ceafe9e4b85f1e15d))
* **vector_db:** add support for keywords in VectorDB and related functions ([d0791f8](https://github.com/Mosqlimate-project/mosqlimate-assistant/commit/d0791f82171769252cba1f6f8ad684831100a187))

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
