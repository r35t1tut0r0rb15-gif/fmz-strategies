# #434285 Full Crypto Swing ALMA Cross MACD Quantitative Strategy -> `fmz_434285_alma_cross_macd_swing`

- FMZ source id: 434285 (lineage).
- Source: https://www.fmz.com/strategy/434285 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 10:24:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent exits fixed at entry (approximation stated) |
| 2 | PASS | ALMA crosses, a MACD slope and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [40, 80]: **4 trials**; ALMA offset / sigma, MACD and the exit percentages fixed.

## Ambiguities resolved

- Close-sized exits fixed at the fill (trailing_stop_pending); side-dependent bracket. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
