import json
from typing import Optional, Union

import ollama
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from openai import OpenAI

from mosqlimate_assistant import faiss_db, schemas, utils
from mosqlimate_assistant.api_consumer import generate_api_url
from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.prompts import por
from mosqlimate_assistant.settings import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    GOOGLE_API_URL,
    OLLAMA_MODEL,
)


class Assistant:
    def make_query(
        self,
        user_input: str,
        examples_list: list[dict[str, str]] = por.EXAMPLES_LIST,
    ) -> str:
        escaped_examples: list[dict[str, str]] = []
        for ex in examples_list:
            escaped_examples.append(
                {
                    "question": ex["question"],
                    "answer": (
                        ex["answer"]
                        .replace("{", "{{")
                        .replace("}", "}}")["answer"]
                        if False
                        else ex["answer"].replace("{", "{{").replace("}", "}}")
                    ),
                }
            )
        example_template = (
            """Exemplo:\nPergunta: {question}\nResposta: {answer}"""
        )

        prefix = f"""{por.BASE_PROMPT}\n{por.TABLE_PROMPT}\n{por.UF_PROMPT}"""

        suffix = """Agora, responda à seguinte pergunta: {user_question}\n"""

        few_shot_prompt = FewShotPromptTemplate(
            examples=escaped_examples,
            example_prompt=PromptTemplate(
                input_variables=["question", "answer"],
                template=example_template,
            ),
            prefix=prefix,
            suffix=suffix,
            input_variables=["user_question"],
        )

        return few_shot_prompt.format(user_question=user_input)

    def clean_output(self, output: Optional[str]) -> dict:
        if output is None:
            raise RuntimeError("Erro ao limpar output: output é None")
        if "```json" in output:
            output = output[output.find("```json") + 7 :]
        elif "</think>" in output:
            output = output[output.find("</think>") + 10 :]

        output = output.replace("```", "")
        output = output[output.rfind("{") : output.rfind("}") + 1]
        output = output.replace("None", "null").strip()
        output = output.replace("{{", "{").replace("}}", "}")

        try:
            return json.loads(output)
        except Exception as e:
            raise RuntimeError(f"Erro ao converter o output em json: {e}")

    def get_table_filters(self, output_json: dict) -> Union[
        schemas.InfodengueFilters,
        schemas.ClimateFilters,
        schemas.MosquitoFilters,
        schemas.EpiscannerFilters,
        schemas.TableFilters,
    ]:
        output_data = schemas.TableFilters(**output_json)
        if output_data.table == "infodengue":
            return schemas.InfodengueFilters(**output_json)
        elif output_data.table == "climate":
            return schemas.ClimateFilters(**output_json)
        elif output_data.table == "mosquito":
            return schemas.MosquitoFilters(**output_json)
        elif output_data.table == "episcanner":
            return schemas.EpiscannerFilters(**output_json)
        return output_data

    def generate_mosqlient_infodengue_code(
        self, filters: schemas.InfodengueFilters
    ) -> str:
        code = f"from mosqlient import get_infodengue\n\n# return a pd.DataFrame with the data\ndf = get_infodengue(start_date='{filters.start}',end_date='{filters.end}',disease='{filters.disease}'"
        if filters.uf:
            code += f",uf='{filters.uf}'"
        if filters.city:
            geocode = get_municipality_code(filters.city, filters.uf)
            code += f",geocode='{geocode}'"
        code += ")"
        return code

    def generate_mosqlient_climate_code(
        self, filters: schemas.ClimateFilters
    ) -> str:
        code = f"from mosqlient import get_climate\n\n# return a pd.DataFrame with the data\ndf = get_climate(start_date='{filters.start}',end_date='{filters.end}'"
        if filters.uf:
            code += f",uf='{filters.uf}'"
        if filters.city:
            geocode = get_municipality_code(filters.city, filters.uf)
            code += f",geocode='{geocode}'"
        code += ")"
        return code

    def get_relevant_sample_asks(
        self, prompt: str, k: int = 3
    ) -> tuple[list[dict[str, str]], float]:
        vector_db = faiss_db.get_or_create_vector_db()
        docs = vector_db.similarity_search_with_score(prompt, k=k)
        samples = [
            {
                "question": doc[0].page_content,
                "answer": utils.format_answer(doc[0].metadata["output"]),
            }
            for doc in docs
        ]
        return samples, float(docs[0][1])

    def make_query_and_get_url(
        self,
        prompt: str,
        threshold: float = 0.8,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> str:
        samples, score = self.get_relevant_sample_asks(prompt)
        if score < threshold:
            raise RuntimeError(
                f"Não foi possível encontrar exemplos relevantes para a pergunta: {prompt}"
            )
        output_json = self.query_llm(prompt, samples, save_logs, save_path)
        table_filters = self.get_table_filters(output_json)
        return generate_api_url(table_filters)

    def query_llm(
        self,
        prompt: str,
        examples_list: list[dict[str, str]] = por.EXAMPLES_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        raise NotImplementedError(
            "query_llm deve ser implementado nas subclasses"
        )


class AssistantOpenAI(Assistant):
    def __init__(
        self,
        api_key: Optional[str] = DEEPSEEK_API_KEY,
        base_url: Optional[str] = DEEPSEEK_API_URL,
    ):
        self.model = OpenAI(api_key=api_key, base_url=base_url)

    def query_llm(
        self,
        prompt: str,
        examples_list: list[dict[str, str]] = por.EXAMPLES_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        full_query = self.make_query(prompt, examples_list)
        output = (
            self.model.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": full_query},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            .choices[0]
            .message
        )
        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(output)],
                save_path,
            )
        return self.clean_output(output.content)


class AssistantOllama(Assistant):
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.model_name = model_name

    def query_llm(
        self,
        prompt: str,
        examples_list: list[dict[str, str]] = por.EXAMPLES_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        full_query = self.make_query(prompt, examples_list)
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": full_query},
                {"role": "user", "content": prompt},
            ],
            format="json",
        )
        output = response["message"]["content"]
        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(output)],
                save_path,
            )
        return self.clean_output(output)


class AssistantGemini(Assistant):
    def __init__(
        self,
        api_key: Optional[str] = GOOGLE_API_KEY,
        base_url: Optional[str] = GOOGLE_API_URL,
    ):
        self.api_key = api_key
        self.model = OpenAI(api_key=api_key, base_url=base_url)

    def query_llm(
        self,
        prompt: str,
        examples_list: list[dict[str, str]] = por.EXAMPLES_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:

        full_query = self.make_query(prompt, examples_list)

        response = self.model.beta.chat.completions.parse(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": full_query},
                {"role": "user", "content": prompt},
            ],
            response_format=schemas.TableFilters,
        )
        parsed = response.choices[0].message.parsed

        if save_logs:

            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(parsed)],
                save_path,
            )

        if isinstance(parsed, schemas.TableFilters):
            return dict(parsed)

        return self.clean_output(parsed)
