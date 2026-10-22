# #440536 基于前一天收盘价和ATR指标的趋势追踪策略Previous-Days-Close-with-ATR-Trend-Tracking-Strategy -> `fmz_440536_prev_close_daily_atr_breakout`

- FMZ source id: 440536 (lineage).
- Source: https://www.fmz.com/strategy/440536 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-31 14:39:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days; bracket fixed at entry |
| 2 | PASS | Daily close, range and ATR levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Size 10 is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entr` [0.8, 0.5] x `tplevel` [1.7, 2.5]: **4 trials**; stop 0.2 ATR and ATR 14 fixed.

## Ambiguities resolved

- Daily references from completed days (the [1] values two days back, as written). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_band_breakout"`.

## Marks

`none`
