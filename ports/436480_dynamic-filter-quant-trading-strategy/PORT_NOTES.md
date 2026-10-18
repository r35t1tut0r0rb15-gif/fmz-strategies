# #436480 Dynamic Filter Quant Trading Strategy -> `fmz_436480_range_filter_flips`

- FMZ source id: 436480 (lineage).
- Source: https://www.fmz.com/strategy/436480 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-25 11:10:09). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C89). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range filter state flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [100, 50] x `mult` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Range filter from zero; display blocks ignored. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
