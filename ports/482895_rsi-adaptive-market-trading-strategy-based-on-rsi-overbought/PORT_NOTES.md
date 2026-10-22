# #482895 基于RSI超买超卖的自适应市场交易策略-Adaptive-Market-Trading-Strategy-Based-on-RSI-Overbought-Oversold -> `fmz_482895_rsi14_30_70_state_utc06_17_pct_bracket_reversal`

- FMZ source id: 482895 (lineage).
- Source: https://www.fmz.com/strategy/482895 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:28:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | RSI extremes inside a clock window |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `tp_percent` [2.0, 3.0]: **4 trials**; levels 30 / 70, stop 1 %, window 06-17 UTC.

## Ambiguities resolved

- The window is read in UTC (the header exchange's zone). Repeat state signals re-send the bracket; pending.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
