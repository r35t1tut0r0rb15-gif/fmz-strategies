# #482780 Hybrid Trading Strategy Based on Volatility Breakout and Multiple Technical Indicators -> `fmz_482780_bb_breakout_sma_cross_volume_atr_bracket_long_only`

- FMZ source id: 482780 (lineage).
- Source: https://www.fmz.com/strategy/482780 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 15:01:24). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Bollinger breakouts on SMA crossings and high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.0] x `tp_atr` [2.0, 3.0]: **4 trials**; BB 20 x 2, SMA 10 / 50, volume x 1.5.

## Ambiguities resolved

- The close is a crossing bar without breakout. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
