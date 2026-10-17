# #485126 零延迟移动平均趋势交叉策略Zero-Lag-Moving-Average-Trend-Crossover-Strategy -> `fmz_485126_zero_lag_ema_cross_long`

- FMZ source id: 485126 (lineage).
- Source: https://www.fmz.com/strategy/485126 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 11:06:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 30]: **2 trials**; default 15 (the source's, its only input).

## Session open (check 9)

The 15:45 `close_all` (chart time zone) never matches a 1-hour bar (minute always 0): it never fires as written and
is not emitted.

## Ambiguities resolved

- Long only, exit on the opposite cross: opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
