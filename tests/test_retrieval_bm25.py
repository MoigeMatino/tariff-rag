from tariff_rag.chunking import chunk_transcript
from tariff_rag.retrieval import BM25Retriever, Hit, tokenize, top_k
from tariff_rag.transcript import load_transcript

CHUNKS = chunk_transcript(load_transcript())


def test_tokenize_splits_currency_and_drops_thousands_separators():
    assert tokenize("Ksh.1,500 flat rate") == ["ksh", "1500", "flat", "rate"]


def test_tokenize_keeps_decimals_and_drops_stopwords():
    assert tokenize("What is the fee for 0.25%?") == ["fee", "0.25"]


def test_top_k_breaks_ties_by_chunk_order():
    hits = top_k(CHUNKS[:3], [1.0, 2.0, 2.0], k=2)
    assert [h.chunk.id for h in hits] == [CHUNKS[1].id, CHUNKS[2].id]
    assert all(isinstance(h, Hit) for h in hits)


def test_bm25_finds_agency_pesalink():
    hits = BM25Retriever(CHUNKS).search("Pesalink charge through an agent", k=1)
    assert hits[0].chunk.section_id == "agency-banking"
    assert "Pesalink" in hits[0].chunk.text


def test_bm25_finds_rtgs_in_the_treasury_table():
    hits = BM25Retriever(CHUNKS).search("outgoing RTGS", k=1)
    assert hits[0].chunk.section_id == "treasury-and-transfers"


def test_bm25_returns_k_hits_best_first():
    hits = BM25Retriever(CHUNKS).search("credit card annual fee", k=3)
    assert len(hits) == 3
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_bm25_returns_nothing_for_a_query_of_only_stopwords():
    assert BM25Retriever(CHUNKS).search("what is the", k=3) == []
