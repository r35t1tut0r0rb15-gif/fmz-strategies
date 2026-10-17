# #489017 双均线趋势追踪量化策略-Dual-EMA-Trend-Following-Quantitative-Strategy -> `fmz_489017_onetrend_lite_v1_ema_gap_cross_long`

- FMZ source id: 489017 (lineage).
- Source: https://www.fmz.com/strategy/489017 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:59:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An EMA gap in ATR units |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group (a later variant is #489311). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`margin_mult` [0.3, 0.6] x `ema_fast` [30, 20]: **4 trials**; defaults 0.3 / 30 (the source's); EMA 60, ATR 60 fixed.

## Ambiguities resolved

- Crosses against the margin's own previous value. Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
