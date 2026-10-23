# #453226 VWAP与超级趋势买卖策略-VWAP-and-Super-Trend-Buy-Sell-Strategy -> `fmz_453226_supertrend_state_close_vs_hl2_alternating_reversal`

- FMZ source id: 453226 (lineage).
- Source: https://www.fmz.com/strategy/453226 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 10:45:14). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend state with the bar's own midpoint |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 20] x `mult` [2.0, 3.0]: **4 trials**.

## Ambiguities resolved

- Daily VWAP = hl2 (volume cancels); alternating flags. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
