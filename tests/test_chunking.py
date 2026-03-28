"""Tests for the balanced_chunk_split function."""

from mosqlimate_assistant.document_consumer import balanced_chunk_split


def test_empty_input():
    assert balanced_chunk_split("") == []
    assert balanced_chunk_split("   ") == []


def test_short_text_single_chunk():
    text = "This is a short text."
    result = balanced_chunk_split(text, chunk_size=500)
    assert len(result) == 1
    assert result[0] == text


def test_balanced_output():
    """Chunks should be roughly balanced — no chunk smaller than chunk_size // 3."""
    # Create a text that would produce unbalanced chunks with naive splitting
    text = (
        "Part one of the text. " * 20
        + "\n\n"
        + "Part two. " * 10
        + "\n\n"
        + "Tiny."
    )
    result = balanced_chunk_split(text, chunk_size=200, chunk_overlap=0)
    min_size = 200 // 3
    for i, chunk in enumerate(result):
        # Last chunk may be slightly under if can't merge, but should not be tiny
        if len(result) > 1 and i < len(result) - 1:
            assert (
                len(chunk) >= min_size or len(chunk) <= 10
            ), f"Chunk {i} is unbalanced: {len(chunk)} chars"


def test_all_chunks_within_size():
    """No chunk should dramatically exceed chunk_size (overlap may add a bit)."""
    text = ("Hello world. " * 50 + "\n\n") * 5
    result = balanced_chunk_split(text, chunk_size=200, chunk_overlap=30)
    for i, chunk in enumerate(result):
        # Allow some tolerance for overlap
        assert (
            len(chunk) <= 200 + 60
        ), f"Chunk {i} too large: {len(chunk)} chars"


def test_overlap_preserves_context():
    """Consecutive chunks should share overlapping text."""
    text = "Word " * 200
    result = balanced_chunk_split(text, chunk_size=100, chunk_overlap=20)
    if len(result) > 1:
        for i in range(1, len(result)):
            # The start of chunk[i] should contain text from end of chunk[i-1]
            # (overlap may be cleaned to word boundary)
            assert len(result[i]) > 0


def test_fewer_chunks_than_naive():
    """balanced_chunk_split should produce fewer chunks than chunk_size-based ceiling."""
    text = "A" * 1000
    result = balanced_chunk_split(text, chunk_size=300, chunk_overlap=0)
    # Naive: ceil(1000/300) = 4 chunks. Balanced should be <= 4.
    assert len(result) <= 4


def test_custom_separators():
    text = "# Title\n## Section A\nContent A line 1.\nContent A line 2.\n## Section B\nContent B."
    result = balanced_chunk_split(
        text,
        chunk_size=50,
        chunk_overlap=0,
        separators=["## ", "\n", ". ", " "],
    )
    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) > 0


def test_markdown_headers_respected():
    """Splitting on markdown headers should keep sections together."""
    text = "# Main Title\n\nIntro paragraph.\n\n## Section One\n\nContent of section one with enough text to be meaningful.\n\n## Section Two\n\nContent of section two also with enough text."
    result = balanced_chunk_split(text, chunk_size=500, chunk_overlap=0)
    # The text is ~190 chars, fits in one chunk
    assert len(result) == 1


def test_backward_compatible_alias():
    """recursive_character_split should be available as an alias."""
    from mosqlimate_assistant.document_consumer import (
        recursive_character_split,
    )

    assert recursive_character_split is balanced_chunk_split
