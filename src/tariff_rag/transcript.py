"""Loads the hand-checked transcription of the tariff poster.

The PDF text layer is unreliable (see DECISIONS.md 003), so the source of truth is a JSON file
transcribed from the rendered poster. This module defines its shape and refuses files that do not
fit it: a row with the wrong number of cells, a region outside the page, or a transcript made from
a different edition of the guide.
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "data" / "transcript" / "tariff_guide.json"
SOURCE_PATH = ROOT / "data" / "source.json"


class Row(BaseModel):
    cells: list[str] = Field(min_length=1)
    group: str | None = None  # a sub-heading inside a table, e.g. "Mail Transfer"


class Section(BaseModel):
    """One table on the poster, with where it sits on the page."""

    id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    title: str
    page: int = Field(ge=1)
    region: tuple[float, float, float, float]  # x0, y0, x1, y1 in PDF points, approximate
    status: Literal["draft", "verified"]
    columns: list[str] = Field(min_length=1)
    rows: list[Row] = Field(min_length=1)
    notes: list[str] = []

    @model_validator(mode="after")
    def rows_match_columns(self) -> "Section":
        for i, row in enumerate(self.rows):
            if len(row.cells) != len(self.columns):
                raise ValueError(
                    f"section {self.id!r} row {i} has {len(row.cells)} cells, "
                    f"expected {len(self.columns)}"
                )
        x0, y0, x1, y1 = self.region
        if not (x0 < x1 and y0 < y1):
            raise ValueError(f"section {self.id!r} region is empty or inverted")
        return self


class Transcript(BaseModel):
    source_sha256: str
    page_size: tuple[float, float]  # width, height in PDF points
    sections: list[Section] = Field(min_length=1)

    @model_validator(mode="after")
    def check_sections(self) -> "Transcript":
        ids = [s.id for s in self.sections]
        if len(ids) != len(set(ids)):
            raise ValueError("section ids must be unique")
        width, height = self.page_size
        for s in self.sections:
            x0, y0, x1, y1 = s.region
            if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
                raise ValueError(f"section {s.id!r} region lies outside the page")
        return self

    def section(self, section_id: str) -> Section:
        for s in self.sections:
            if s.id == section_id:
                return s
        raise KeyError(section_id)


def load_transcript(path: Path = DEFAULT_PATH, source_path: Path = SOURCE_PATH) -> Transcript:
    """Reads and validates the transcript, and checks it was made from the pinned edition."""
    transcript = Transcript.model_validate_json(path.read_text())
    pinned = json.loads(source_path.read_text())["sha256"]
    if transcript.source_sha256 != pinned:
        raise ValueError(
            f"{path.name} was transcribed from a different edition "
            f"({transcript.source_sha256[:12]}...) than the pinned one ({pinned[:12]}...)"
        )
    return transcript
