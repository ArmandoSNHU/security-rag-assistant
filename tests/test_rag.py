from secrag.embeddings import HashingEmbeddings
from secrag.llm import ExtractiveLLM
from secrag.rag import Document, RagEngine


def _engine():
    return RagEngine(HashingEmbeddings(dim=256), ExtractiveLLM(), chunk_size=60, overlap=10)


DOCS = [
    Document(
        source="mitre.md",
        text="MITRE ATT&CK maps adversary techniques to identifiers such as T1190 for "
             "exploiting a public facing application. Detection engineers cite the technique ID.",
    ),
    Document(
        source="gdpr.md",
        text="GDPR governs personal data protection, lawful basis, consent, and breach "
             "notification to the supervisory authority within seventy two hours.",
    ),
    Document(
        source="pci.md",
        text="PCI DSS requires protecting cardholder data, network segmentation, and "
             "quarterly external vulnerability scans by an approved scanning vendor.",
    ),
]


def test_ingest_counts_chunks():
    engine = _engine()
    n = engine.ingest(DOCS)
    assert n == len(DOCS)          # each short doc is one chunk
    assert len(engine.store) == 3


def test_retrieval_picks_the_right_source():
    engine = _engine()
    engine.ingest(DOCS)

    result = engine.answer("Which technique ID maps an adversary exploit?", k=3)
    assert result["citations"][0]["source"] == "mitre.md"

    result = engine.answer("How long until a personal data breach must be reported?", k=3)
    assert result["citations"][0]["source"] == "gdpr.md"

    result = engine.answer("How often are cardholder vulnerability scans required?", k=3)
    assert result["citations"][0]["source"] == "pci.md"


def test_answer_has_citations_and_text():
    engine = _engine()
    engine.ingest(DOCS)
    result = engine.answer("What does MITRE ATT&CK do?", k=2)
    assert result["answer"]
    assert 1 <= len(result["citations"]) <= 2
    assert result["citations"][0]["n"] == 1
    assert "score" in result["citations"][0]
