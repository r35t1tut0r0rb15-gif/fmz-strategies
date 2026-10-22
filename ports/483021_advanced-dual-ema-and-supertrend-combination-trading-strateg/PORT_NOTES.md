# #483021 Advanced Dual EMA and Supertrend Combination Trading Strategy -> `fmz_483021_ema5_20_cross_supertrend3_10_long`

- FMZ source id: 483021 (lineage).
- Source: https://www.fmz.com/strategy/483021 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:20:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a SuperTrend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [5, 9] x `factor` [3.0, 2.0]: **4 trials**; EMA 20, ATR 10.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
