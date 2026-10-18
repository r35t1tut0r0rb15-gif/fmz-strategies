# #436146 Short term Trading Strategy Based on Chaikin Volatility Indicator -> `fmz_436146_chaikin_volatility_sign`

- FMZ source id: 436146 (lineage).
- Source: https://www.fmz.com/strategy/436146 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-21 16:14:56). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility rate of change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length` [10, 14]: **4 trials**; rate of change 12 fixed.

## Ambiguities resolved

- State changes only. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_band"`.

## Marks

`none`
