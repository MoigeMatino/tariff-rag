# Step 1: source inspection

Source: Co-op-A2-Bank-Tariff-Guide_9-September-2026.pdf (sha256 0458c6257367...)
Pages: 1, size 1191 x 1684 pt, producer: Adobe Illustrator 30.8 (Macintosh)

## Text layer health

| Measure | pdfplumber | pdfplumber dedupe | PyMuPDF | pdftotext |
|---|---|---|---|---|
| Characters extracted | 48627 | 41792 | 21378 | 33448 |
| Repeated lines (share) | 15% | 10% | 45% | 49% |
| Garbled lines | 11 | 6 | 25 | 25 |

Glyphs drawn more than once at the same position: 17% of 41829.

## Probes: does each extractor match what a person sees?

| Phrase | On poster | pdfplumber | pdfplumber dedupe | PyMuPDF | pdftotext | Note |
|---|---|---|---|---|---|---|
| Purchase of Treasury Bills | visible | 0 | 0 | 0 | 0 | Treasury section, bottom of column 1 |
| Pesalink Transactions | visible | 0 | 0 | 0 | 0 | Agency table row label |
| Above 1,000 | visible | 0 | 0 | 2 | 1 | Agency Pesalink fee band |
| 200,001-999,999 | hidden | 1 | 1 | 0 | 2 | Tiered Pesalink band not drawn on the poster |
| 10th February | hidden | 0 | 0 | 0 | 1 | Date line from an earlier edition |
| 9th September 2026 | visible | 1 | 1 | 1 | 0 | Current edition date line |

## Sample garbled lines

- `N#&O')*2)&>>0/$&;*2) ?'%@CDD)>0"')$&'%)%&230/28)$%&#8(')GI%(#()&>>0/$&40(J)`
- `7*"#/(#)$%&#8(')G&')>(#)I%&5)%&')4((2)$%&#8(3)4-)5%()'(#:/$()>#*:/3(#)`
- `9*:(#26(25)'($"#/;(')+*#)#(5&/0)/2:('5*#')5%#*"8%)5%()4&2<=')`
- `F*#(/82)7"##(2$-)N#&O')GP2)?'%)*#)QR"/:&0(25)/2)F*#(E))`
- `?'%@CDD)>0"')$&'%)%&230/28)$%&#8(')GI%(#()&>>0/$&40(J)`

Rendered 12 tiles to reports/tiles/ for visual review.
