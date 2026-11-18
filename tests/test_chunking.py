from tariff_rag.chunking import chunk_section, chunk_transcript, item_blocks, pack_blocks
from tariff_rag.transcript import Row, Section, load_transcript


def section(rows, columns=("Service", "Range (Ksh.)", "Cost")):
    return Section(
        id="agency-banking",
        title="Agency Tariff Guide",
        page=1,
        region=(36, 522, 393, 798),
        status="draft",
        columns=list(columns),
        rows=[Row(**r) for r in rows],
    )


def withdrawal_bands(n):
    return [{"cells": ["Cash withdrawals", f"band {i}", f"Ksh.{i}"]} for i in range(n)]


def test_headers_travel_with_every_value():
    chunks = chunk_section(section([{"cells": ["Pesalink Transactions", "Above 1,000", "Ksh.20"]}]))
    assert "Range (Ksh.): Above 1,000 | Cost: Ksh.20" in chunks[0].text
    assert chunks[0].text.startswith("Section: Agency Tariff Guide")


def test_empty_cells_are_left_out_of_row_text():
    chunks = chunk_section(section([{"cells": ["Balance Inquiry", "", "Ksh.10"]}]))
    assert "Service: Balance Inquiry | Cost: Ksh.10" in chunks[0].text


def test_bands_of_one_item_are_never_split():
    rows = withdrawal_bands(7) + [{"cells": [f"Other {i}", "", "Ksh.50"]} for i in range(8)]
    chunks = chunk_section(section(rows), max_rows=6)
    holding_bands = [c for c in chunks if "Cash withdrawals" in c.text]
    assert len(holding_bands) == 1
    assert holding_bands[0].text.count("Cash withdrawals") == 7


def test_rows_under_one_sub_heading_stay_together():
    rows = [{"group": "Drafts", "cells": [f"line {i}", "Ksh.1"]} for i in range(3)]
    rows += [{"group": "RTGS", "cells": [f"line {i}", "Ksh.2"]} for i in range(3)]
    assert item_blocks(section(rows, columns=("Service", "Charges")).rows) == [(0, 3), (3, 6)]


def test_split_is_balanced_not_full_then_leftover():
    blocks = [(i, i + 1) for i in range(13)]
    assert pack_blocks(blocks, max_rows=12) == [(0, 7), (7, 13)]


def test_every_row_appears_in_exactly_one_chunk():
    for s in load_transcript().sections:
        chunks = chunk_section(s)
        covered = [i for c in chunks for i in range(c.row_start, c.row_end)]
        assert covered == list(range(len(s.rows))), s.id


def test_chunks_never_mix_sections_and_carry_citation_fields():
    for c in chunk_transcript(load_transcript()):
        assert c.text.startswith("Section: ")
        assert c.page == 1
        assert c.citation().startswith("Page 1, ")
        assert c.id.startswith(c.section_id + "-")


def test_chunk_ids_are_stable_and_unique():
    first = [c.id for c in chunk_transcript(load_transcript())]
    second = [c.id for c in chunk_transcript(load_transcript())]
    assert first == second
    assert len(first) == len(set(first))


def test_agency_pesalink_bands_share_a_chunk():
    agency = chunk_section(load_transcript().section("agency-banking"))
    pesalink = [c for c in agency if "Pesalink" in c.text]
    assert len(pesalink) == 1
    assert "0-1,000" in pesalink[0].text and "Above 1,000" in pesalink[0].text
