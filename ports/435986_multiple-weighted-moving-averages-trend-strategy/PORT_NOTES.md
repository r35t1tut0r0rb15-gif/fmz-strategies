# #435986 Multiple Weighted Moving Averages Trend Strategy -> `fmz_435986_wma_order_stack`

- FMZ source id: 435986 (lineage).
- Source: https://www.fmz.com/strategy/435986 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 15:59:56). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Weighted average order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop and risk inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435986. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [29, 20] x `len2` [5, 8]: **4 trials**; WMA 3 / 2 / 1 fixed.

## Ambiguities resolved

- Header period 30m (title says 3 minutes); exits off. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
