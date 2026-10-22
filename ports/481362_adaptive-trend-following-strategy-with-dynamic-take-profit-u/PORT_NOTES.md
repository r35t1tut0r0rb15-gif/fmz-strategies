# #481362 Adaptive Trend Following Strategy with Dynamic Take Profit Using Multiple Technical Indicators -> `fmz_481362_macd_crossup_ema50_200_rsi70_long_no_exit`

- FMZ source id: 481362 (lineage).
- Source: https://www.fmz.com/strategy/481362 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:59:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the condition-armed stop described (pending) |
| 2 | PASS | MACD cross-ups in an EMA up-trend with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop percentage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [50, 20] x `rsi_overbought` [70, 80]: **4 trials**; EMA 200, MACD 12 / 26 / 9; the armed stop pending.

## Ambiguities resolved

- The danger-armed stop is kept pending; no exit, as #437800. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`
