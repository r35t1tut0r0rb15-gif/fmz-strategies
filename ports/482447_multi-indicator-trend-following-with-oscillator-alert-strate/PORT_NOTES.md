# #482447 Multi Indicator Trend Following with Oscillator Alert Strategy -> `fmz_482447_sma20_200_cross_adx20_stoch_numbers_tick_trail_reversal`

- FMZ source id: 482447 (lineage).
- Source: https://www.fmz.com/strategy/482447 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:54:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | PASS | SMA crossings with ADX and an as-written stochastic filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [20, 25] x `trail_pct` [1.19048e-05, 1.19048e-03]: **4 trials**; SMA 20 / 200, activation 40 ticks.

## Ambiguities resolved

- ta.stoch(close, 14, 3, 3) as written (numbers as high / low); ticks at the 0.1 tick as fractions of 42000.
- The fill-bar reversal block uses the signal bar before, not the trail state. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop`
