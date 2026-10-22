# #451702 MA Rejection Strategy with ADX Filter -> `fmz_451702_wma50_rejection_wma_adx_filter_reversal`

- FMZ source id: 451702 (lineage).
- Source: https://www.fmz.com/strategy/451702 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 10:35:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WMA rejections with an ADX filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [50, 100] x `adx_min` [20, 25]: **8 trials**; the WMA 20 and the ADX length 14 fixed.

## Ambiguities resolved

- Hand-made WMA ADX. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
