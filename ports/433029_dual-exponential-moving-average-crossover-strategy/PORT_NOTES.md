# #433029 Dual Exponential Moving Average Crossover Strategy -> `fmz_433029_dema_8_20_63_state`

- FMZ source id: 433029 (lineage).
- Source: https://www.fmz.com/strategy/433029 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 17:34:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short` [8, 5] x `long2` [63, 100]: **4 trials**; DEMA 20 of the lows fixed.

## Ambiguities resolved

- Level entries, state held otherwise. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
