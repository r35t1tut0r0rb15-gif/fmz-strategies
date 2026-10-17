# #488134 多时间框架抛物线SAR动态趋势跟踪量化策略-Multi-Timeframe-Parabolic-SAR-Dynamic-Trend-Following-Quantitative-Strategy -> `fmz_488134_sar_flip_daily_sar_agree`

- FMZ source id: 488134 (lineage).
- Source: https://www.fmz.com/strategy/488134 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 13:22:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed daily values. |
| 2 | PASS | SAR. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_max` [0.2, 0.1] x `sar_inc` [0.02, 0.01]: **4 trials**; defaults 0.2 / 0.02 (the source's); SAR start 0.02; the
same settings on both timeframes, as written.

## Ambiguities resolved

- The daily SAR (`request.security("D", ..., lookahead_off)`) is the last completed broker day's (house rule, as
  #430771), built from the port's bars grouped by broker day.
- The show-inputs default to both on: only the two-timeframe rule applies. Closes act on the position at the bar's
  start (#430850). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
