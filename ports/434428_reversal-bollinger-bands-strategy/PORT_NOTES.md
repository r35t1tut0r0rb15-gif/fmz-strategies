# #434428 Reversal-Bollinger-Bands-Strategy反转波动带策略 -> `fmz_434428_bollinger_extreme_range_bracket`

- FMZ source id: 434428 (lineage).
- Source: https://www.fmz.com/strategy/434428 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 11:20:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-issued levels approximated) |
| 2 | PASS | Bollinger extremes and range levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434428. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 40] x `range_len` [10, 20]: **4 trials**; 2 deviations fixed.

## Ambiguities resolved

- Signal-bar levels re-based on the fill; re-issued levels on repeat signals not ported (trailing_stop_pending). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
