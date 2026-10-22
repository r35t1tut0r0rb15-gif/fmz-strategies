# #481093 Momentum Adaptive Gaussian Channel Multi Period Strategy -> `fmz_481093_gaussian144_channel_breakout_stochrsi_season_long`

- FMZ source id: 481093 (lineage).
- Source: https://www.fmz.com/strategy/481093 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-08 14:49:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gaussian-channel breakouts with Stochastic RSI and a seasonal filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk 0.5 % / ATR 22 qty stored, not ported; commission not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_gc` [144, 89] x `multiplier` [1.414, 2.0]: **4 trials**; poles 4, Stoch RSI 14 / 14 / 3 / 80, season Sep-Feb.

## Ambiguities resolved

- The filter seeds from 0 (nz), as written; season by UTC month. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_band"`.

## Marks

`none`
