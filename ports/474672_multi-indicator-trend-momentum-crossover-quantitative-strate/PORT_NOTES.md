# #474672 Multi Indicator Trend Momentum Crossover Quantitative Strategy -> `fmz_474672_ema9_21_cross_supertrend_dir_rsi_long`

- FMZ source id: 474672 (lineage).
- Source: https://www.fmz.com/strategy/474672 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-11 15:00:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with supertrend and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_mult` [3.0, 2.0] x `st_len` [10, 20]: **4 trials**; EMA / RSI settings fixed.

## Ambiguities resolved

- Direction tests as written (Pine direction 1 = down-trend). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
