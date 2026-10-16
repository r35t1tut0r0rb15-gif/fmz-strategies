# #429467 Adaptive Trend Tracking Stop Loss Strategy -> `fmz_429467_wilder_volatility_line`

- FMZ source id: 429467 (lineage).
- Source: https://www.fmz.com/strategy/429467 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 14:04:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [3.0, 2.0] x `atr_length` [7, 14]: **4 trials**; close as the significant price fixed.

## Ambiguities resolved

- The else branch gives 0 as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
