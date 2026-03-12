from mosqlimate_assistant.embeddings import (
    BaseEmbeddingProvider,
    OllamaEmbeddingProvider,
)


class DummyEmbeddingProvider(BaseEmbeddingProvider):
    def embed_query(self, text: str):
        if len(text) > 10:
            return []
        return [0.1, 0.2]


def test_safe_embed():
    provider = DummyEmbeddingProvider()
    res = provider.safe_embed("short")
    assert res == [0.1, 0.2]

    # Should fallback by halving string size until it's less than 10 characters
    res2 = provider.safe_embed("this is a very long string that should be cut")
    assert res2 == [0.1, 0.2]


def test_normalize():
    vec = [3.0, 4.0]
    norm_vec = OllamaEmbeddingProvider._normalize(vec)
    # The norm is 5, so it should be [0.6, 0.8]
    assert abs(norm_vec[0] - 0.6) < 1e-6
    assert abs(norm_vec[1] - 0.8) < 1e-6
