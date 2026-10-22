# #439843 Moving Average Divergence Strategy -> `fmz_439843_wma14_regular_hidden_divergence`

- FMZ source id: 439843 (lineage).
- Source: https://www.fmz.com/strategy/439843 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 11:43:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots known after the right lookback |
| 2 | PASS | WMA pivots and price pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [14, 21] x `lb` [5, 3]: **4 trials**; the same lookback on both sides; range 2-600 fixed.

## Ambiguities resolved

- Strict pivots. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
