# #440537 Supertrend BarUpDn Fusion Strategy -> `fmz_440537_gap_candle_reversal`

- FMZ source id: 440537 (lineage).
- Source: https://www.fmz.com/strategy/440537 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 14:43:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gap candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gap_lag` [1]: **1 trial**; the author's supertrend inputs do not change the orders, so one trial.

## Ambiguities resolved

- Supertrend has no effect as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
