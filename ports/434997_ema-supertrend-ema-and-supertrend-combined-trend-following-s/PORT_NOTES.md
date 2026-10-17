# #434997 EMA与SuperTrend组合趋势跟踪策略EMA-and-SuperTrend-Combined-Trend-Following-Strategy -> `fmz_434997_supertrend_swapped_ema34`

- FMZ source id: 434997 (lineage).
- Source: https://www.fmz.com/strategy/434997 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 15:49:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands and an average side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [10.0, 2.0] x `atr_len` [2, 10]: **4 trials**; EMA 34 fixed (factor 2 / ATR 10 is the intended setting).

## Ambiguities resolved

- Swapped Supertrend arguments as written (intended owed). Same-bar entry beats the close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
