# #433959 Volatility Stop Tracking Strategy -> `fmz_433959_volatility_stop_flips`

- FMZ source id: 433959 (lineage).
- Source: https://www.fmz.com/strategy/433959 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-01 17:53:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 3.0]: **4 trials**.

## Ambiguities resolved

- Seeds of 0 as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
