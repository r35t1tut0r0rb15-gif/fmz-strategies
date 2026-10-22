# #471695 Combined Momentum SMA Crossover Strategy with Market Sentiment and Resistance Level Optimization System -> `fmz_471695_sma10_30_cross_macd_exit_at_closing_high_long`

- FMZ source id: 471695 (lineage).
- Source: https://www.fmz.com/strategy/471695 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:10:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a resistance exit |
| 3 | PASS | Exchange pair in the header only (XAUUSD named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 5] x `long_len` [30, 50] x `res_len` [20, 50]: **8 trials**.

## Ambiguities resolved

- The short-side close never acts (as written). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
