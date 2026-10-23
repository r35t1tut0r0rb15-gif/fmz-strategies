# #435282 Dual directional Trading Strategy Based on Quantitative Indicators Bullish and Bearish Signals -> `fmz_435282_filtered_obv_osc_channel_breakout_trail_reversal`

- FMZ source id: 435282 (lineage).
- Source: https://www.fmz.com/strategy/435282 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 17:30:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop and house trail from the fill |
| 2 | PASS | Price and OBV-oscillator channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x leverage 2 / close x risk 100 %, commission 0.075 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel_length` [65, 40] x `osc_length` [40, 20]: **4 trials**; filter 20 x 1.2, fast channel 70 %, stop 3.75 %, trail 2.5 % / 2.5 %.

## Ambiguities resolved

- Leverage-halved percentages; house trail from minute highs. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`coarse_bar_stop, trailing_stop`
