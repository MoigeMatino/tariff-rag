"""Checks that data/raw holds exactly the tariff guide edition this project is pinned to."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    source = json.loads((ROOT / "data" / "source.json").read_text())
    pdf = ROOT / "data" / "raw" / source["filename"]
    if not pdf.exists():
        print(f"Missing {pdf.relative_to(ROOT)}. Download it from: {source['download_url']}")
        return 1
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != source["sha256"]:
        print(f"Hash mismatch for {pdf.name}.\n  expected {source['sha256']}\n  got      {digest}")
        print("The bank may have republished the guide. Do not update the hash without review.")
        return 1
    print(f"OK {pdf.name} matches the pinned edition ({source['captured_as_of']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
