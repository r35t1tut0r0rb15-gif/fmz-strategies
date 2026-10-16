# #429564 Relative Body Index Crossover Strategy -> `fmz_429564_relative_body_index`

- FMZ source id: 429564 (lineage).
- Source: https://www.fmz.com/strategy/429564 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-18 11:16:53). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated). |
| 2 | ADAPT | Tick distances -> ATR multiples / a fraction. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and slippage stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`par1` [5, 10] x `sl_atr` [0.03, 1.0]: **4 trials**; signal 5, thresholds 0 and the trail fixed.

## Ambiguities resolved

- Tick exits as ATR multiples / fractions (stated). REVERSAL INTENDED. Marks coarse_bar_stop, trailing_stop.
- FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop`
