# #440552 Bilateral Three Point Moving Average Quantitative Trading Strategy -> `fmz_440552_finite_volume_elements_direction_reversal`

- FMZ source id: 440552 (lineage).
- Source: https://www.fmz.com/strategy/440552 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-31 16:11:41). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Finite-volume-element direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [22, 50] x `factor` [0.3, 0.1]: **4 trials**.

## Ambiguities resolved

- FVE as written (starts at 0 once the volume SMA exists). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`
