# #438787 Dual Moving Average Reversal Trading Strategy -> `fmz_438787_reversal123_ema2_20_combo`

- FMZ source id: 438787 (lineage).
- Source: https://www.fmz.com/strategy/438787 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-15 12:35:29). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and EMA band position |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `ma_length` [20, 40]: **4 trials**; K smoothing 1, D 3, level 50 fixed.

## Ambiguities resolved

- 123 test as written; disagreement closes. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
