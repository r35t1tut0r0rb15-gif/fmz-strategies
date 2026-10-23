# #483680 Exponential Moving Average Candle Stop Trading Strategy -> `fmz_483680_candle_stop_trend_close_stop_flag_reversal`

- FMZ source id: 483680 (lineage).
- Source: https://www.fmz.com/strategy/483680 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 11:11:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked stop in the signals |
| 2 | PASS | Trend-side candle-stop reversals with a close-based stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.025, 0.05] x `shadow` [0.8, 1.0]: **4 trials**; EMA 20 / 90, RSI 14 >= 70 for shorts.

## Ambiguities resolved

- The script's flag and the real position can part ways (exit side from the current trend). Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`none`
