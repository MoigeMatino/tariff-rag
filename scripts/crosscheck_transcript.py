"""Lists transcript amounts that the PDF text layer does not contain, for a person to review.

A miss is not an error. The Treasury region, for example, is unreadable in the text layer, so its
amounts are expected to miss. A miss in a section with a healthy text layer is worth a second
look at the rendered poster: it may be a transcription typo.
"""

import json
import re
from pathlib import Path

import pymupdf

from tariff_rag.transcript import load_transcript

ROOT = Path(__file__).resolve().parents[1]
AMOUNT = re.compile(r"\d(?:[\d,]*\d)?(?:\.\d+)?%?")


def amounts(cell: str) -> list[str]:
    """Numbers worth checking: anything with three or more digits, a decimal or a percent sign.
    Small bare numbers like "4" or "10" match almost anywhere, so checking them proves nothing."""
    found = AMOUNT.findall(cell)
    return [a for a in found if len(a.replace(",", "")) >= 3 or "." in a or "%" in a]


def in_text(amount: str, text: str) -> bool:
    """True if the amount appears as a whole number, so "500" does not match inside "1,500"."""
    return re.search(rf"(?<!\d)(?<!\d[,.]){re.escape(amount)}(?!\d|,\d)", text) is not None


def main() -> None:
    source = json.loads((ROOT / "data" / "source.json").read_text())
    page = pymupdf.open(ROOT / "data" / "raw" / source["filename"])[0]

    total_checked = total_missing = 0
    for section in load_transcript().sections:
        # Search only this section's region, so "1,500" elsewhere on the poster cannot count.
        text = " ".join(page.get_text(clip=pymupdf.Rect(section.region)).split())
        checked = sorted({a for row in section.rows for cell in row.cells for a in amounts(cell)})
        missing = [a for a in checked if not in_text(a, text)]
        total_checked += len(checked)
        total_missing += len(missing)
        print(f"{section.id}: {len(checked) - len(missing)}/{len(checked)} amounts found")
        for a in missing:
            print(f"  not in text layer: {a}")
    print(f"\n{total_missing} of {total_checked} amounts not found in the PDF text layer.")


if __name__ == "__main__":
    main()
