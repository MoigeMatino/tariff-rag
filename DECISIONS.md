# Decisions

One entry per decision: what we chose, what we rejected, and the evidence. Newest last.

## 001. Keep the retrieval index in memory for v1

Status: accepted

The corpus is one tariff poster, a few hundred rows at most, written once at ingestion and read on
every query. Brute-force cosine similarity over a few hundred vectors plus BM25 over the same rows
fits in memory and needs no infrastructure. The index sits behind a `Retriever` interface so a
database can replace it if the corpus grows.

Rejected: TidesDB, an embeddable key-value storage engine built on an LSM tree and optimised for
write-heavy workloads. Our workload is read-only and we need similarity and keyword search, which
it does not provide. Rejected for now: PostgreSQL with pgvector, which adds a service to run
without a measured need.

## 002. Pin one edition of the tariff guide by hash

Status: accepted

The bank republishes the guide and older editions stay online. Expected answers in the eval are
only valid for one edition. `data/source.json` records the file name, capture date and SHA-256 of
the edition we use, and `make verify-source` fails on any other file. The PDF is not committed to
the repo; it is downloaded from the bank's site.

## 003. Do not trust the PDF text layer as the source of truth

Status: accepted (finding). The ingestion approach that follows from it is proposed in 004.

The guide is a single A2 poster exported from Adobe Illustrator. `make inspect` shows:

- 17% of glyphs are drawn more than once at the same position, so extractors read stacked copies.
- Between 10% and 49% of substantial lines repeat, depending on the extractor.
- The Treasury and foreign transfer section is visible on the poster but extracts as runs of
  punctuation in every extractor tested, so text search can never find it.
- Text that is not drawn on the poster is still in the file: a tiered Pesalink table up to
  "200,001-999,999" and a "10th February" date line from an earlier edition. The poster shows a
  different Pesalink table (0-1,000 free, above 1,000 Ksh.20).
- Words containing the "ti" ligature lose those letters ("Transactions" becomes "Transac?ons"),
  so even visible labels like "Pesalink Transactions" fail exact search.

Consequence: a pipeline that chunks extracted text would retrieve fees nobody can see on the
poster and miss sections everybody can see. The ground truth must come from what is rendered.

## 004. Ingest from a checked transcription of the rendered poster

Status: accepted

Follows from 003. The text layer cannot be the source of truth, so the poster is transcribed from
rendered crops into `data/transcript/tariff_guide.json`, one section per table with its region on
the page. Each section starts as `draft` and becomes `verified` only after the owner compares it
with the poster. The transcript records the SHA-256 of the edition it was made from, and loading
fails on a mismatch.

The text layer is still used as a cross-check: `make crosscheck` searches each table's region for
the amounts in that table. On the first transcript, every amount in the four readable tables was
found and none of the six Treasury amounts were, which matches 003.

Rejected: chunking text extracted with pdfplumber or PyMuPDF, for the reasons in 003. Rejected for
now: OCR of the rendered poster, which adds a dependency and its own errors, for a corpus small
enough to transcribe and check by hand.

Known limit: the transcript is written by the same assistant that drafts the eval answers, so the
owner's review of both is the independent check. Until then, no result counts.

## 005. Chunk by table, write rows as column-value pairs

Status: accepted

Fee tables lose their meaning when a value is separated from its header or band. Each chunk holds
rows from one table only, every row repeats its column names, and tables over 12 rows split into
balanced parts between items, never inside one (all seven agency withdrawal bands stay together).
Chunk ids are `<section>-<nn>` so they stay stable for citations and eval results.
