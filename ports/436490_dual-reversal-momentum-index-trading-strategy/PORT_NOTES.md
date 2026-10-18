# #436490 Dual Reversal Momentum Index Trading Strategy -> `fmz_436490_noro_stochastic_smi_extremes`

- FMZ source id: 436490 (lineage).
- Source: https://www.fmz.com/strategy/436490 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 12:02:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C89). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic momentum index and candle colour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital percent and the lot formula stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [5, 10] x `limit` [50, 40]: **4 trials**; %D length 3 fixed.

## Ambiguities resolved

- Position-dependent exit; orders in call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
