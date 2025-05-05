import json
import os

from mosqlimate_assistant.settings import MOSQLIMATE_API_DOCS


def save_logs(logs: list[str], save_path: str = ".") -> None:
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    save_file = os.path.join(save_path, "prompt_logs.txt")
    with open(save_file, "a") as file:
        for log in logs:
            file.write(log)
            file.write("\n")
        file.write("\n\n")


def get_mosqlimate_api_docs() -> dict:
    import requests

    response = requests.get(MOSQLIMATE_API_DOCS)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(
            f"Erro ao obter a documentação da API: {response.status_code}"
        )


def format_answer(answer: str) -> str:
    ans_dict = json.loads(answer)
    answer = "```json\n"
    answer += json.dumps(ans_dict, indent=2) + "\n```"

    return answer
