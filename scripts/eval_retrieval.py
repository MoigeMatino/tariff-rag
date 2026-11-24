"""Compares retrievers on eval/questions.json and writes reports/retrieval_eval.md.

Retrieval only: no language model is called, so this needs no API key. The answer key is a
draft until the owner has checked it, and the report says so.
"""

import json
from pathlib import Path
from statistics import mean

from tariff_rag.chunking import chunk_transcript
from tariff_rag.embeddings import FastEmbedder
from tariff_rag.evaluation import (
    first_relevant_rank,
    hit_at_k,
    mean_reciprocal_rank,
    random_hit_at_k,
)
from tariff_rag.retrieval import BM25Retriever, Retriever, VectorRetriever
from tariff_rag.transcript import load_transcript

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "retrieval_eval.md"


def build_retrievers(chunks) -> list[Retriever]:
    return [
        BM25Retriever(chunks),
        VectorRetriever(chunks, FastEmbedder()),
        VectorRetriever(chunks, FastEmbedder(query_prefix="")),
    ]


def fmt(x: float) -> str:
    return f"{x:.2f}"


def main() -> None:
    eval_set = json.loads((ROOT / "eval" / "questions.json").read_text())
    questions = eval_set["questions"]
    answerable = [q for q in questions if q["type"] == "answerable"]
    fallback = [q for q in questions if q["type"] == "fallback"]
    chunks = chunk_transcript(load_transcript())
    retrievers = build_retrievers(chunks)
    n = len(chunks)

    def n_relevant(q):
        return sum(c.section_id == q["expected_section"] for c in chunks)

    ranks: dict[str, list[int | None]] = {}
    top_scores: dict[str, tuple[list[float], list[float]]] = {}
    for r in retrievers:
        ranks[r.name] = [
            first_relevant_rank(r.search(q["question"], k=n), q["expected_section"])
            for q in answerable
        ]

        def top(q, r=r):
            hits = r.search(q["question"], k=1)
            return hits[0].score if hits else 0.0

        top_scores[r.name] = ([top(q) for q in answerable], [top(q) for q in fallback])

    lines = [
        "# Retrieval eval",
        "",
        f"Answer key status: **{eval_set['status']}**. Scores are provisional until the owner "
        "has checked the expected answers.",
        f"Corpus: {n} chunks from {len({c.section_id for c in chunks})} sections "
        "(poster column 1 only). A hit is any chunk from the question's expected section.",
        "",
        f"## Answerable questions ({len(answerable)})",
        "",
        "| Retriever | Hit@1 | Hit@3 | MRR |",
        "|---|---|---|---|",
    ]
    for name, rs in ranks.items():
        lines.append(
            f"| {name} | {fmt(hit_at_k(rs, 1))} | {fmt(hit_at_k(rs, 3))} | "
            f"{fmt(mean_reciprocal_rank(rs))} |"
        )
    random_at_1 = mean(random_hit_at_k(n_relevant(q), n, 1) for q in answerable)
    random_at_3 = mean(random_hit_at_k(n_relevant(q), n, 3) for q in answerable)
    lines.append(f"| random ranking (expected) | {fmt(random_at_1)} | {fmt(random_at_3)} | n/a |")

    lines += ["", "Rank of the first chunk from the expected section (1 is best):", ""]
    lines += ["| Question | Expected section | " + " | ".join(ranks) + " |"]
    lines += ["|---|---|" + "---|" * len(ranks)]
    for i, q in enumerate(answerable):
        cells = " | ".join(str(ranks[name][i] or "miss") for name in ranks)
        lines.append(f"| {q['id']} {q['question']} | {q['expected_section']} | {cells} |")

    lines += [
        "",
        f"## Can a score threshold detect fallback questions? ({len(fallback)} questions)",
        "",
        "Top-1 score per question. A threshold can only separate the two groups if every "
        "fallback question scores below every answerable one.",
        "",
        "| Retriever | Answerable: lowest top score | Fallback: highest top score | Separable |",
        "|---|---|---|---|",
    ]
    for name, (ans, fb) in top_scores.items():
        separable = "yes" if max(fb) < min(ans) else "no"
        lines.append(f"| {name} | {min(ans):.3f} | {max(fb):.3f} | {separable} |")

    lines += ["", "| Question | " + " | ".join(top_scores) + " |"]
    lines += ["|---|" + "---|" * len(top_scores)]
    for i, q in enumerate(fallback):
        cells = " | ".join(f"{top_scores[name][1][i]:.3f}" for name in top_scores)
        lines.append(f"| {q['id']} {q['question']} | {cells} |")

    REPORT.write_text("\n".join(lines) + "\n")
    print(REPORT.read_text())


if __name__ == "__main__":
    main()
