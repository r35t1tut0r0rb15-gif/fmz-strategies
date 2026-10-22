# #488165 Multi Timeframe Exponential Moving Average Crossover Strategy with Trend Confirmation System -> `fmz_488165_close_ema50_cross_ema200_dmi_utc_window_pct_bracket_reversal`

- FMZ source id: 488165 (lineage).
- Source: https://www.fmz.com/strategy/488165 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 16:58:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | ADAPT | Tick bracket read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.2, 0.4] x `sl_pct` [0.1, 0.2]: **4 trials**; EMA 50 / 200, DMI 14, 16:30-20:00 UTC.

## Ambiguities resolved

- Ticks read as percents at ETH 3000. Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
