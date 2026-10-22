# #440361 基于EMA指标的跨周期交易策略EMA-Crossover-Quantitative-Trading-Strategy -> `fmz_440361_ema11_21_intraday_long_levels`

- FMZ source id: 440361 (lineage).
- Source: https://www.fmz.com/strategy/440361 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 15:56:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested levels |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [1.0, 2.0] x `target_pct` [3.0, 1.5]: **4 trials**; EMA 11 / 21 and hour 15 fixed.

## Ambiguities resolved

- Script flag kept as written; hours read on the UTC bar open. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
