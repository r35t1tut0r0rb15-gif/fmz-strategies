# #439233 Quant Trading Support and Resistance Cloud Indicator -> `fmz_439233_rang3r_range_extreme_as_written`

- FMZ source id: 439233 (lineage).
- Source: https://www.fmz.com/strategy/439233 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-18 15:30:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range highs and lows with a ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_period` [50, 25] x `sensitivity` [0.9999, 0.999]: **4 trials**.

## Ambiguities resolved

- Long / short swapped as written (intended version owed). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
