# #427925 ATR Trailing Stop Strategy -> `fmz_427925_atr_band_reversal`

- FMZ source id: 427925 (lineage).
- Source: https://www.fmz.com/strategy/427925 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 20:23:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.
- Duplicate group: **DG427925** (3 members, best partner #442844, Jaccard 0.899); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427925. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [26, 50] x `mul` [1, 2] x `mullow` [2, 1]: **8 trials**; defaults 26 / 1 / 2 (the source's).

## Ambiguities resolved

- sma(close, 1) = close; the date window is open. Nothing trails despite the title.
- Closes coincide with the opposite entries: REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
