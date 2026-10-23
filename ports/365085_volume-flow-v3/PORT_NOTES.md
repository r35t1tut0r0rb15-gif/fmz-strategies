# #365085 Volume Flow v3 -> `fmz_365085_bull_bear_volume_spike_x3_reversal`

- FMZ source id: 365085 (lineage).
- Source: https://www.fmz.com/strategy/365085 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-23 14:40:50). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Colour-split volume spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 30] x `x` [3.1, 2.0]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
