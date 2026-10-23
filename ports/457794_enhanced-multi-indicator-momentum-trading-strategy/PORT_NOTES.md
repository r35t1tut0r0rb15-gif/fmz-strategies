# #457794 Enhanced Multi Indicator Momentum Trading Strategy -> `fmz_457794_three_candle_run_volume_surge_ema200_atr_bracket_reversal`

- FMZ source id: 457794 (lineage).
- Source: https://www.fmz.com/strategy/457794 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 16:20:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal bar as fractions of the fill |
| 2 | PASS | Three-candle runs on a volume surge with an EMA 200 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_ratio` [1.5, 2.0] x `tp_atr` [2.5, 4.0]: **4 trials**; volume period 3, SL 1.5 ATR, EMA 200.

## Ambiguities resolved

- Bracket fixed at the signal bar. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
