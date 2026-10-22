# #482848 Volatility Momentum Breakout Strategy with Trend and Momentum Filters -> `fmz_482848_prev20_channel_atr1_5_break_ema50_rsi50_atr_bracket_reversal`

- FMZ source id: 482848 (lineage).
- Source: https://www.fmz.com/strategy/482848 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:13:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | ATR-padded channel breaks with EMA / RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity stored, not ported (riskPercent unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.5, 1.0] x `lookback` [20, 40]: **4 trials**; ATR 14, EMA 50, RSI 14 / 50, stop 1 ATR, RR 2.

## Ambiguities resolved

- The bracket re-sent with the current ATR is fixed at the signal bar's ATR from the fill; pending.
- The stale entry price after a reversal is not copied (each bracket uses its own fill). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`trailing_stop_pending`
