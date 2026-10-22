# #457776 动态Keltner通道动量反转策略-Dynamic-Keltner-Channel-Momentum-Reversal-Strategy -> `fmz_457776_keltner_touch_then_middle_pullback_reversal`

- FMZ source id: 457776 (lineage).
- Source: https://www.fmz.com/strategy/457776 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 15:02:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ATR stop as a fraction of the signal close; re-issued stops pending (mark) |
| 2 | PASS | Keltner middle-line pullbacks after an outer touch |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [6.0, 3.0] x `ema_len` [280, 100] x `lookback` [120, 50]: **8 trials**; the ATR 35 and the 5.5 stop fixed.

## Ambiguities resolved

- Re-issued stops pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
