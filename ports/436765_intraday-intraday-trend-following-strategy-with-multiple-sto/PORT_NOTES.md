# #436765 融合多重止损的趋势追踪型Intraday策略Intraday-Trend-Following-Strategy-with-Multiple-Stop-Loss -> `fmz_436765_triple_vstop_renko_step_long`

- FMZ source id: 436765 (lineage).
- Source: https://www.fmz.com/strategy/436765 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 15:30:07). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 4-hour values end with the daily bar |
| 2 | PASS | Volatility stops and ATR steps |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vlen` [26, 40] x `renko_atr` [60, 30]: **4 trials**; the multipliers 5 / 10 / 15 and the 4-hour frame fixed.

## Ambiguities resolved

- Lower time frame from a daily chart = the day's last 4-hour bar, 4-hour bars counted from the broker day's start; nz seeds as written; short side commented out. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
