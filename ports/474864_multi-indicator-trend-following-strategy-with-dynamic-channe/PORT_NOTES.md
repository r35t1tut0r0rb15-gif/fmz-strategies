# #474864 Multi Indicator Trend Following Strategy with Dynamic Channel and Moving Average Trading System -> `fmz_474864_g_channel100_ema50_alternating_atr_bracket_reversal`

- FMZ source id: 474864 (lineage).
- Source: https://www.fmz.com/strategy/474864 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:58:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | G-Channel state against an EMA with alternating signals and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `ema_length` [50, 100]: **4 trials**; ATR 14, 2 / 4.

## Ambiguities resolved

- Cross tests as written; nz seeds of 0. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`coarse_bar_stop`
