import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data" / "source.json").read_text())
PDF = ROOT / "data" / "raw" / SOURCE["filename"]


@pytest.mark.skipif(not PDF.exists(), reason="source PDF not downloaded")
def test_source_pdf_matches_pinned_hash():
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == SOURCE["sha256"]
