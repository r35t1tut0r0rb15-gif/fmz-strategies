# #435269 Supertrend Blind Following Strategy -> `fmz_435269_supertrend_line_cross`

- FMZ source id: 435269 (lineage).
- Source: https://www.fmz.com/strategy/435269 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-13 16:49:44). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility trend line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `pd` [7, 14]: **4 trials**.

## Ambiguities resolved

- Wilder ATR; crossings of the active line. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
