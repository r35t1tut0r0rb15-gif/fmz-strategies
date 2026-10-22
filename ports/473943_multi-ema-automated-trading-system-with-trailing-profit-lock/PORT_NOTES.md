# #473943 Multi EMA Automated Trading System with Trailing Profit Lock -> `fmz_473943_stacked_ema5_20hlc_50_breakout_long`

- FMZ source id: 473943 (lineage).
- Source: https://www.fmz.com/strategy/473943 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-04 15:35:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked EMA breakouts with close-based exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the EMA lengths are constants).

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
