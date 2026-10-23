# #435091 Volume Oscillator Long and Short Term Moving Average Crossover Strategy -> `fmz_435091_volume_oscillator_swing_size_zero_cross_reversal`

- FMZ source id: 435091 (lineage).
- Source: https://www.fmz.com/strategy/435091 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-12 11:19:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume oscillator swing comparison at zero crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`shortlen` [5, 10] x `longlen` [10, 20]: **4 trials**.

## Ambiguities resolved

- Swing levels start at 0 (inputs). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_oscillator"`.

## Marks

`none`
