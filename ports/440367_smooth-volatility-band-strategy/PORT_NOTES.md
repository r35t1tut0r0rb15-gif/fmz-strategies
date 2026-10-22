# #440367 Smooth Volatility Band Strategy -> `fmz_440367_range_filter_trend_daily`

- FMZ source id: 440367 (lineage).
- Source: https://www.fmz.com/strategy/440367 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 16:22:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range filter of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [100, 50] x `mult` [3.0, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "range_filter_trend"`.

## Marks

`none`
