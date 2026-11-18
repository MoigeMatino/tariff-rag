"""Turns transcript sections into retrieval chunks without breaking fee tables apart.

Rules:
- A chunk never mixes two sections.
- Every row is written as "column: value" pairs, so the header travels with each value.
  "Above 1,000 | Ksh.20" becomes "Range (Ksh.): Above 1,000 | Cost: Ksh.20".
- Large tables are split into groups of rows, but only between items. The seven cash withdrawal
  bands share one label and always land in the same chunk, even if that chunk runs over the limit.
  Rows under one sub-heading (a row group) are kept together the same way.
- Chunk ids depend only on section id and position, so they stay stable between runs.
"""

import math
from dataclasses import dataclass

from tariff_rag.transcript import Row, Section, Transcript

MAX_ROWS = 12


@dataclass(frozen=True)
class Chunk:
    id: str
    section_id: str
    section_title: str
    page: int
    region: tuple[float, float, float, float]
    row_start: int  # index of the first row in the section, inclusive
    row_end: int  # index after the last row, exclusive
    text: str

    def citation(self) -> str:
        return f"Page {self.page}, {self.section_title}"


def row_text(columns: list[str], row: Row) -> str:
    pairs = [f"{col}: {cell}" for col, cell in zip(columns, row.cells, strict=True) if cell]
    line = " | ".join(pairs)
    return f"[{row.group}] {line}" if row.group else line


def item_blocks(rows: list[Row]) -> list[tuple[int, int]]:
    """Groups consecutive rows that describe one item: the same sub-heading if the rows have
    one, otherwise the same label in the first column."""
    blocks: list[tuple[int, int]] = []
    start = 0
    for i in range(1, len(rows) + 1):
        if i == len(rows) or _item_key(rows[i]) != _item_key(rows[start]):
            blocks.append((start, i))
            start = i
    return blocks


def _item_key(row: Row) -> str:
    return row.group if row.group else row.cells[0]


def pack_blocks(blocks: list[tuple[int, int]], max_rows: int) -> list[tuple[int, int]]:
    """Fills chunks with whole blocks, aiming for chunks of even size.

    A 13-row table with max_rows=12 becomes about 7 + 6 rows rather than 12 + 1.
    """
    total = blocks[-1][1] - blocks[0][0] if blocks else 0
    n_chunks = max(1, math.ceil(total / max_rows))
    limit = math.ceil(total / n_chunks)
    spans: list[tuple[int, int]] = []
    for start, end in blocks:
        if spans and end - spans[-1][0] <= limit:
            spans[-1] = (spans[-1][0], end)
        else:
            spans.append((start, end))
    return spans


def chunk_section(section: Section, max_rows: int = MAX_ROWS) -> list[Chunk]:
    header = [f"Section: {section.title}", "Columns: " + " | ".join(section.columns)]
    header += [f"Note: {note}" for note in section.notes]
    chunks = []
    for n, (start, end) in enumerate(pack_blocks(item_blocks(section.rows), max_rows), 1):
        body = [row_text(section.columns, row) for row in section.rows[start:end]]
        chunks.append(
            Chunk(
                id=f"{section.id}-{n:02d}",
                section_id=section.id,
                section_title=section.title,
                page=section.page,
                region=section.region,
                row_start=start,
                row_end=end,
                text="\n".join(header + body),
            )
        )
    return chunks


def chunk_transcript(transcript: Transcript, max_rows: int = MAX_ROWS) -> list[Chunk]:
    return [c for s in transcript.sections for c in chunk_section(s, max_rows)]
