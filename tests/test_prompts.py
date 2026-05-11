from mosqlimate_assistant.prompts import get_single_agent_prompt


def test_get_single_agent_prompt():
    prompt = get_single_agent_prompt()
    assert isinstance(prompt, str)
    assert "ferramentas" in prompt.lower()
    assert "Mosqlimate" in prompt
    assert "batch_document_search" in prompt
    assert "2 a 4 blocos" in prompt
