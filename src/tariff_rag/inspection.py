"""Measures how trustworthy a PDF's text layer is before we build on it.

Each function returns a number or a list we can print in a report and assert on in tests.
"""

import re
from collections import Counter
from collections.abc import Iterable, Mapping


def is_garbled(line: str, min_alnum_share: float = 0.5) -> bool:
    """A line is garbled when most of its visible characters are not letters or digits.

    Broken font encodings tend to come out as runs of ASCII punctuation, so a fee line
    like "Ksh.1,500 flat rate" passes and "!\"#$%&'()*+),#(&'" fails.
    """
    visible = [c for c in line if not c.isspace()]
    if len(visible) < 10:
        return False
    alnum = sum(c.isalnum() for c in visible)
    return alnum / len(visible) < min_alnum_share


def garbled_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if is_garbled(line)]


def duplicate_line_share(text: str, min_len: int = 15) -> float:
    """Share of substantial lines that appear more than once in the extracted text."""
    lines = [" ".join(line.split()) for line in text.splitlines()]
    lines = [line for line in lines if len(line) >= min_len]
    if not lines:
        return 0.0
    counts = Counter(lines)
    repeated = sum(n for n in counts.values() if n > 1)
    return repeated / len(lines)


def stacked_char_share(chars: Iterable[Mapping], precision: int = 0) -> float:
    """Share of characters drawn again at the same spot with the same glyph.

    A clean PDF draws each glyph once. Design tools that paste layers on top of each
    other leave copies at identical coordinates, which text extractors read twice.
    """
    keys = [
        (c["text"], round(c["x0"], precision), round(c["top"], precision))
        for c in chars
        if not c["text"].isspace()
    ]
    if not keys:
        return 0.0
    counts = Counter(keys)
    extra = sum(n - 1 for n in counts.values() if n > 1)
    return extra / len(keys)


def phrase_count(text: str, phrase: str) -> int:
    """Case-insensitive count that tolerates the irregular spacing extractors produce."""
    words = [re.escape(w) for w in phrase.split()]
    pattern = r"\s+".join(words)
    return len(re.findall(pattern, text, flags=re.IGNORECASE))
