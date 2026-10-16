# #430148 Gradient Trailing Stop Loss Strategy -> `fmz_430148_supertrend_inverted`

- FMZ source id: 430148 (lineage).
- Source: https://www.fmz.com/strategy/430148 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 14:56:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR band. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 15 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [10, 20] x `factor` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- The direction mapping is kept as written (short in Pine's up-trend). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
