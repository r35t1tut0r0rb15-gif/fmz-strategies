# #458274 Supertrend和EMA交叉量化交易策略Supertrend-and-EMA-Crossover-Quantitative-Trading-Strategy -> `fmz_458274_close_cross_ema44_against_supertrend_1pct_bracket_reversal`

- FMZ source id: 458274 (lineage).
- Source: https://www.fmz.com/strategy/458274 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:43:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | EMA crossings against the Supertrend direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The size cap and the equity share stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [44, 21] x `factor` [3.0, 2.0] x `bracket` [0.01, 0.03]: **8 trials**; the ATR 10 fixed.

## Ambiguities resolved

- Direction > 0 is Pine's down trend (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
