# #431407 Dual Moving Average Reversal Tracking System -> `fmz_431407_combo_123_ichimoku2c`

- FMZ source id: 431407 (lineage).
- Source: https://www.fmz.com/strategy/431407 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-07 16:00:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A stochastic and Donchian midpoints |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `displacement` [26, 13]: **4 trials**; K 1, D 3, level 50 and Ichimoku 9 / 26 / 52 fixed.

## Ambiguities resolved

- Spans as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
