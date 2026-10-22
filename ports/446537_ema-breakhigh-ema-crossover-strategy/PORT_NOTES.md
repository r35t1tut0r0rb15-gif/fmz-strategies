# #446537 突破最高价EMA交叉策略-BreakHigh-EMA-Crossover-Strategy -> `fmz_446537_34bar_high_break_daily_ema34_exit_long`

- FMZ source id: 446537 (lineage).
- Source: https://www.fmz.com/strategy/446537 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 14:39:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the daily EMA from completed broker days |
| 2 | PASS | Channel-high breakouts with a daily EMA exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-per-trade quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [34, 52] x `daily_ema` [34, 20]: **4 trials**; the stop switch off.

## Ambiguities resolved

- Daily EMA from completed broker days. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
