from secrag.chunk import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("one two three", size=120) == ["one two three"]


def test_empty_text_yields_no_chunks():
    assert chunk_text("   ") == []


def test_long_text_splits_with_overlap():
    words = [f"w{i}" for i in range(300)]
    text = " ".join(words)
    chunks = chunk_text(text, size=120, overlap=20)
    assert len(chunks) >= 3
    # every chunk is at most `size` words
    assert all(len(c.split()) <= 120 for c in chunks)
    # consecutive chunks share the overlap window
    first_tail = chunks[0].split()[-20:]
    second_head = chunks[1].split()[:20]
    assert first_tail == second_head


def test_invalid_overlap_rejected():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("a b c", size=10, overlap=10)
