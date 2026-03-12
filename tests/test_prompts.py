from mosqlimate_assistant.prompts import (
    get_base_docs_prompt,
    get_coder_agent_prompt,
    get_imdc_agent_prompt,
)


def test_get_base_docs_prompt():
    prompt = get_base_docs_prompt()
    assert isinstance(prompt, str)
    assert "Mosqlimate" in prompt
    assert "COMO VOCÊ DEVE SE COMPORTAR" in prompt


def test_get_coder_agent_prompt():
    prompt = get_coder_agent_prompt()
    assert isinstance(prompt, str)
    assert (
        "exemplo de código" in prompt.lower()
        or "exemplos de código" in prompt.lower()
    )
    assert "mosqlient" in prompt.lower()


def test_get_imdc_agent_prompt():
    prompt = get_imdc_agent_prompt()
    assert isinstance(prompt, str)
    assert "IMDC" in prompt
    assert "Infodengue" in prompt
