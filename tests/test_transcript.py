import json

import pytest
from pydantic import ValidationError

from tariff_rag.transcript import Section, Transcript, load_transcript


def make_section(**overrides):
    data = {
        "id": "agency-banking",
        "title": "Agency Tariff Guide",
        "page": 1,
        "region": [36, 522, 393, 798],
        "status": "draft",
        "columns": ["Service", "Range (Ksh.)", "Cost"],
        "rows": [{"cells": ["Pesalink Transactions", "Above 1,000", "Ksh.20"]}],
    }
    data.update(overrides)
    return data


def test_real_transcript_loads_and_matches_pinned_edition():
    transcript = load_transcript()
    assert len(transcript.sections) >= 5
    assert transcript.section("agency-banking").title == "Agency Tariff Guide"


def test_all_sections_start_as_draft_until_checked_by_hand():
    # Flip a section to "verified" only after comparing it with the rendered poster.
    statuses = {s.status for s in load_transcript().sections}
    assert statuses <= {"draft", "verified"}


def test_row_with_wrong_cell_count_is_rejected():
    with pytest.raises(ValidationError, match="expected 3"):
        Section.model_validate(make_section(rows=[{"cells": ["Pesalink Transactions", "Ksh.20"]}]))


def test_inverted_region_is_rejected():
    with pytest.raises(ValidationError, match="empty or inverted"):
        Section.model_validate(make_section(region=[393, 522, 36, 798]))


def test_region_outside_page_is_rejected():
    with pytest.raises(ValidationError, match="outside the page"):
        Transcript.model_validate(
            {
                "source_sha256": "x",
                "page_size": [100, 100],
                "sections": [make_section()],
            }
        )


def test_duplicate_section_ids_are_rejected():
    with pytest.raises(ValidationError, match="unique"):
        Transcript.model_validate(
            {
                "source_sha256": "x",
                "page_size": [1190.55, 1683.78],
                "sections": [make_section(), make_section()],
            }
        )


def test_transcript_from_another_edition_is_rejected(tmp_path):
    path = tmp_path / "transcript.json"
    path.write_text(
        json.dumps(
            {
                "source_sha256": "0" * 64,
                "page_size": [1190.55, 1683.78],
                "sections": [make_section()],
            }
        )
    )
    with pytest.raises(ValueError, match="different edition"):
        load_transcript(path)
