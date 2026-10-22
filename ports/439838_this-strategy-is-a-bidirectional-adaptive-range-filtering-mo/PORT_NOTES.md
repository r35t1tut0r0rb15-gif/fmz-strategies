# #439838 This strategy is a bidirectional adaptive range filtering momentum tracking strategy -> `fmz_439838_dw_range_filter_close_flip`

- FMZ source id: 439838 (lineage).
- Source: https://www.fmz.com/strategy/439838 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 11:32:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range filter on closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439838. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rng_qty` [2.618, 1.5] x `rng_per` [14, 28]: **4 trials**; smoothing 27 and averaging 2 fixed.

## Ambiguities resolved

- Conditional EMAs seeded at their first value. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
