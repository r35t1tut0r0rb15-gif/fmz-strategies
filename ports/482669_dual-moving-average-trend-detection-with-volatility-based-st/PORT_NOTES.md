# #482669 Dual Moving Average Trend Detection with Volatility Based Stop Loss Strategy -> `fmz_482669_ema9_21_cross_entry_atr15_stop_reversal`

- FMZ source id: 482669 (lineage).
- Source: https://www.fmz.com/strategy/482669 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:57:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the entry price as a fraction of the fill |
| 2 | PASS | EMA crossings with an ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 3.0] x `ema_slow_len` [21, 50]: **4 trials**; EMA 9, ATR 14.

## Ambiguities resolved

- The per-bar ATR re-set of the stop is pending; the port uses the signal bar's ATR.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
