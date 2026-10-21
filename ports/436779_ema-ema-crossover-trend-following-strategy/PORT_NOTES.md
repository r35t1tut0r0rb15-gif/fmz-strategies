# #436779 基于EMA指标的趋势跟踪策略EMA-Crossover-Trend-Following-Strategy -> `fmz_436779_ema_cross_long_only`

- FMZ source id: 436779 (lineage).
- Source: https://www.fmz.com/strategy/436779 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 16:31:15). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [20, 50]: **4 trials**.

## Ambiguities resolved

- Date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
