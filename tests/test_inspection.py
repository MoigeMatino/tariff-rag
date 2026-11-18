from tariff_rag.inspection import (
    duplicate_line_share,
    garbled_lines,
    is_garbled,
    phrase_count,
    stacked_char_share,
)


def test_fee_lines_are_not_garbled():
    assert not is_garbled("Ksh.1,500 flat rate plus excise duty")
    assert not is_garbled("0.25% for amounts above USD 5,000")


def test_broken_font_encoding_is_garbled():
    assert is_garbled("!\"#$%&'()*+),#(&'\"#-)./00'1)")


def test_short_lines_are_ignored():
    # Table rules and stray digits ("00 - - - -") are layout noise, not encoding failures.
    assert not is_garbled("00 - - - -")


def test_garbled_lines_picks_only_bad_lines():
    text = "Cash withdrawals\n7%&#8(')\nKsh.50\n?'%@ABCDD)+0&5)#&5()>0\n"
    assert garbled_lines(text) == ["?'%@ABCDD)+0&5)#&5()>0"]


def test_duplicate_line_share_counts_repeats():
    text = "Minimum opening balance Ksh.500\n" * 3 + "Maintenance fee for all balances\n"
    assert duplicate_line_share(text) == 0.75


def test_stacked_chars_detect_layered_copies():
    chars = [{"text": "K", "x0": 10.2, "top": 5.1}, {"text": "K", "x0": 10.4, "top": 5.0}]
    chars.append({"text": "s", "x0": 15.0, "top": 5.0})
    assert stacked_char_share(chars) == 1 / 3


def test_phrase_count_tolerates_spacing_and_case():
    assert phrase_count("Gold  Package\nCharges GOLD package", "gold package") == 2
