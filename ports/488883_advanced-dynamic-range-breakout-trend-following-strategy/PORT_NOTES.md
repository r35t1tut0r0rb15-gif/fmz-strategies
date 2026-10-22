# #488883 Advanced Dynamic Range Breakout Trend Following Strategy -> `fmz_488883_keltner20_2_breakout_ema200_rsi_atr_bracket_ema_exit_reversal`

- FMZ source id: 488883 (lineage).
- Source: https://www.fmz.com/strategy/488883 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 15:43:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Keltner breakouts with trend / RSI filters, ATR bracket and EMA exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `length` [20, 30]: **4 trials**; EMA 200, RSI 14, ATR 14 bracket 1.5 / 2.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
