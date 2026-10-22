# #444034 Range Filter Buy Sell Signals Strategy -> `fmz_444034_range_filter_direction_flip_reversal`

- FMZ source id: 444034 (lineage).
- Source: https://www.fmz.com/strategy/444034 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 17:06:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range-filter direction changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG444034. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rng_per` [20, 50] x `rng_qty` [3.5, 2.0]: **4 trials**.

## Ambiguities resolved

- No exit sent, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
