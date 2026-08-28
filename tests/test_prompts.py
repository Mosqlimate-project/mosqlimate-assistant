from mosqlimate_assistant.prompts import get_single_agent_prompt


def test_get_single_agent_prompt():
    prompt = get_single_agent_prompt()
    assert isinstance(prompt, str)
    assert "ferramentas" in prompt.lower()
    assert "Mosqlimate" in prompt
    assert "batch_document_search" in prompt
    assert "2 a 4 blocos" in prompt


def test_get_single_agent_prompt_describes_optional_epidbot_delegation():
    prompt = get_single_agent_prompt(epidbot_enabled=True)

    assert "epidbot_search" in prompt
    assert "fora do escopo" in prompt
    assert "histórico completo" in prompt
    assert "tabelas Markdown" in prompt
    assert "não solicite nem gere imagens" in prompt


def test_get_single_agent_prompt_hides_disabled_epidbot():
    assert "epidbot_search" not in get_single_agent_prompt()
