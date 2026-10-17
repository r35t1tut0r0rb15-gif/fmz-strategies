# #433024 Bollinger Bands Breakout short term trend following Strategy -> `fmz_433024_bb_breakout_vol_filter_trail`

- FMZ source id: 433024 (lineage).
- Source: https://www.fmz.com/strategy/433024 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-23 17:01:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket and a house trail (approximation stated) |
| 2 | PASS | Band crosses, a stdev filter and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The exit percentages quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [15, 30] x `trail_pct` [0.005, 0.02]: **4 trials**; BB 2 sd, stdev filter 15 / 15, SL 2 %, TP 9 % and the 2 % activation fixed.

## Ambiguities resolved

- House percent trail from the fill (the source re-sizes from each close). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop`
