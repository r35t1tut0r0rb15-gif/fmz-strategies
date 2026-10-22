# #488020 Multi Indicator Confirmation Dynamic Trailing Breakout Quantitative Trading Strategy -> `fmz_488020_ema15_40_breakout_rsi_macd_atr_stop_72bar_exit_flat`

- FMZ source id: 488020 (lineage).
- Source: https://www.fmz.com/strategy/488020 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:20:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR stop as a fraction of the fill; bar-count close |
| 2 | PASS | EMA breakouts with RSI / MACD / ATR filters, ATR stop and time exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized leveraged quantity and margins stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaFast` [15, 10] x `maxHoldBars` [72, 24]: **4 trials**; EMA 40, ATR 14, RSI 14, MACD 12 / 26 / 9, stop 1.2 ATR.

## Ambiguities resolved

- Entries only from flat (a loop follows the stop on the bar's high / low); the stop is fixed at the signal bar. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_breakout"`.

## Marks

`none`
