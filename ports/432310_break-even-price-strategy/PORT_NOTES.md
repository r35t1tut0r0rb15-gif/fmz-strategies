# #432310 Break even Price Strategy -> `fmz_432310_sma_14_28_cross`

- FMZ source id: 432310 (lineage).
- Source: https://www.fmz.com/strategy/432310 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 11:16:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 7] x `slow` [28, 56]: **4 trials**.

## Ambiguities resolved

- The break-even lines are display only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
