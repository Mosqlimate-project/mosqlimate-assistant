import json
import re

import pandas as pd
import requests
from mosqlimate_assistant.prompts import por
from mosqlimate_assistant.settings import CODE_REFERENCES_PATH
from typing import Optional


def fetch_file_content(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Erro ao buscar o arquivo {url}: {e}"


def process_documentation_file(
    base_url: str, doc_path: str, file_content: str
) -> str:
    # Processa inclusões de arquivos (--8<--)
    for match in re.finditer(r'--8<-- "(.*?)"', file_content):
        include_path = match.group(1)
        included_content = fetch_file_content(base_url + include_path)
        file_content = file_content.replace(match.group(0), included_content)

    # Processa referências do mkdocstrings (:::)
    for match in re.finditer(r"::: ([\w\._]+)", file_content):
        module_path = match.group(1)
        py_file_path = module_path.replace(".", "/") + ".py"
        module_content_url = base_url + py_file_path
        module_content = fetch_file_content(module_content_url)
        replacement = (
            f"\n---\n"
            f"*Conteúdo de `{py_file_path}`:*\n\n"
            f"```python\n{module_content}\n```\n"
        )
        file_content = file_content.replace(match.group(0), replacement)

    # Processa Jupyter Notebooks
    if doc_path.endswith(".ipynb"):
        try:
            notebook = json.loads(file_content)
            markdown_output = ""
            for cell in notebook.get("cells", []):
                source = "".join(cell.get("source", []))
                if cell.get("cell_type") == "markdown":
                    markdown_output += source + "\n\n"
                elif cell.get("cell_type") == "code":
                    lang = (
                        notebook.get("metadata", {})
                        .get("kernelspec", {})
                        .get("language", "python")
                    )
                    markdown_output += f"```{lang}\n{source}\n```\n\n"
            return markdown_output
        except json.JSONDecodeError:
            return f"Erro: Não foi possível decodificar o JSON do notebook {doc_path}"

    return file_content


def fetch_full_documentation_from_csv(csv_path: str) -> str:
    df = pd.read_csv(csv_path)
    final_output = ""

    for index, row in df.iterrows():
        name = row["name"]
        github_url = row["markdown_link"]
        reference_link = row["url_link"]

        parts = github_url.split("/")
        repo_base_index = parts.index("mosqlimate-client") + 2
        base_url = "/".join(parts[:repo_base_index]) + "/"
        doc_path = "/".join(parts[repo_base_index:])

        final_output += f"# {name}\n"
        final_output += f"[Link de Referência]({reference_link})\n\n"

        file_content = fetch_file_content(github_url)
        processed_content = process_documentation_file(
            base_url, doc_path, file_content
        )

        final_output += processed_content + "\n---\n"
    return final_output.strip()


def build_coder_agent_system_prompt() -> str:
    docs_content = fetch_full_documentation_from_csv(CODE_REFERENCES_PATH)
    prompt = por.BASE_DOCS_PROMPT
    prompt += f"\n\n# Documentação Fornecida\n{docs_content}\n"
    return prompt


def build_coder_agent_user_prompt(
    task_description: str, code_details: Optional[str] = None
) -> str:
    prompt = f"# Descrição da tarefa\n{task_description}\n"
    if code_details:
        prompt += f"\n## Detalhes adicionais\n{code_details}\n"
    return prompt


def tool_call_coder_agent(
    task_description: str, code_details: str = ""
) -> str:
    return json.dumps(
        {"task_description": task_description, "code_details": code_details}
    )
