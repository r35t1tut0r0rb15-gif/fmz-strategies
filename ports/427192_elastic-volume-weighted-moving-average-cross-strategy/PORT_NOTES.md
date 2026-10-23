# #427192 Elastic Volume Weighted Moving Average Cross Strategy -> `fmz_427192_evwma5_40_cross_reversal`

- FMZ source id: 427192 (lineage).
- Source: https://www.fmz.com/strategy/427192 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 22:08:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Elastic volume-weighted average cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [5, 10] x `length2` [40, 20]: **4 trials**.

## Ambiguities resolved

- The averages start from 0, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
