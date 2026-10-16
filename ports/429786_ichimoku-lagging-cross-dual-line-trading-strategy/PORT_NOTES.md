# #429786 Ichimoku Lagging Cross Dual Line Trading Strategy -> `fmz_429786_ichimoku_tk_cross`

- FMZ source id: 429786 (lineage).
- Source: https://www.fmz.com/strategy/429786 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 17:17:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Line crosses from the bars only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427806. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv` [9, 7] x `base` [26, 22]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
