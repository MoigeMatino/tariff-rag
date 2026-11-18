"""Step 1: inspect the tariff guide before choosing an ingestion approach.

Writes reports/inspection.md and renders page tiles to reports/tiles/ for visual review.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pdfplumber
import pymupdf

from tariff_rag.inspection import (
    duplicate_line_share,
    garbled_lines,
    phrase_count,
    stacked_char_share,
)

ROOT = Path(__file__).resolve().parents[1]
TILE_GRID = (3, 4)  # columns x rows, matches the poster's three-column layout

# Phrases checked against each extractor. "visible" is what a person sees on the poster,
# confirmed by eye on the rendered tiles. Update this list as you find more cases.
PROBES = [
    ("Purchase of Treasury Bills", "visible", "Treasury section, bottom of column 1"),
    ("Pesalink Transactions", "visible", "Agency table row label"),
    ("Above 1,000", "visible", "Agency Pesalink fee band"),
    ("200,001-999,999", "hidden", "Tiered Pesalink band not drawn on the poster"),
    ("10th February", "hidden", "Date line from an earlier edition"),
    ("9th September 2026", "visible", "Current edition date line"),
]


def pdftotext(pdf_path: Path) -> str | None:
    """Poppler's extractor, if installed. It reads text the other two miss."""
    if not shutil.which("pdftotext"):
        return None
    result = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    return result.stdout


def render_tiles(page: pymupdf.Page, out_dir: Path, dpi: int = 110) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cols, rows = TILE_GRID
    w, h = page.rect.width / cols, page.rect.height / rows
    paths = []
    for r in range(rows):
        for c in range(cols):
            clip = pymupdf.Rect(c * w, r * h, (c + 1) * w, (r + 1) * h)
            path = out_dir / f"tile_r{r + 1}_c{c + 1}.png"
            page.get_pixmap(dpi=dpi, clip=clip).save(path)
            paths.append(path)
    return paths


def main() -> None:
    source = json.loads((ROOT / "data" / "source.json").read_text())
    pdf_path = ROOT / "data" / "raw" / source["filename"]

    doc = pymupdf.open(pdf_path)
    page = doc[0]
    with pdfplumber.open(pdf_path) as pdf:
        pl_page = pdf.pages[0]
        stacked = stacked_char_share(pl_page.chars)
        n_chars = len(pl_page.chars)
        extractors = {
            "pdfplumber": pl_page.extract_text() or "",
            "pdfplumber dedupe": pl_page.dedupe_chars().extract_text() or "",
            "PyMuPDF": page.get_text(),
        }
    poppler = pdftotext(pdf_path)
    if poppler is not None:
        extractors["pdftotext"] = poppler

    tiles = render_tiles(page, ROOT / "reports" / "tiles")
    garbled = [g for text in extractors.values() for g in garbled_lines(text)]
    names = list(extractors)
    header = "| " + " | ".join(names) + " |"
    rule = "|" + "---|" * (len(names) + 1)

    lines = [
        "# Step 1: source inspection",
        "",
        f"Source: {source['filename']} (sha256 {source['sha256'][:12]}...)",
        f"Pages: {doc.page_count}, size {page.rect.width:.0f} x {page.rect.height:.0f} pt, "
        f"producer: {doc.metadata.get('creator', 'unknown')}",
        "",
        "## Text layer health",
        "",
        "| Measure " + header,
        rule,
        "| Characters extracted | " + " | ".join(str(len(t)) for t in extractors.values()) + " |",
        "| Repeated lines (share) | "
        + " | ".join(f"{duplicate_line_share(t):.0%}" for t in extractors.values())
        + " |",
        "| Garbled lines | "
        + " | ".join(str(len(garbled_lines(t))) for t in extractors.values())
        + " |",
        "",
        f"Glyphs drawn more than once at the same position: {stacked:.0%} of {n_chars}.",
        "",
        "## Probes: does each extractor match what a person sees?",
        "",
        "| Phrase | On poster " + header + " Note |",
        rule + "---|---|",
    ]
    for phrase, seen, note in PROBES:
        counts = " | ".join(str(phrase_count(t, phrase)) for t in extractors.values())
        lines.append(f"| {phrase} | {seen} | {counts} | {note} |")
    lines += ["", "## Sample garbled lines", ""]
    worst = sorted(set(garbled), key=len, reverse=True)[:5]
    lines += [f"- `{g[:80]}`" for g in worst] or ["- none"]
    lines += ["", f"Rendered {len(tiles)} tiles to reports/tiles/ for visual review."]

    out = ROOT / "reports" / "inspection.md"
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())


if __name__ == "__main__":
    main()
