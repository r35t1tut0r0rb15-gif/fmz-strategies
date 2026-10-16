# #430674 定投Golden趋势追踪策略Golden-Trend-Tracking-Strategy-Based-on-Periodic-Investment -> `fmz_430674_dip_finder_one_bar_long`

- FMZ source id: 430674 (lineage).
- Source: https://www.fmz.com/strategy/430674 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 15:09:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close_all every bar as written. |
| 2 | ADAPT | The inert price-unit distance cap dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out cash order size and pyramiding stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [200, 100] x `macd_fast` [12, 8]: **4 trials**; MACD slow 26 fixed.

## Ambiguities resolved

- close_all every bar: one-bar holds, as written. The inert price-unit cap dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
