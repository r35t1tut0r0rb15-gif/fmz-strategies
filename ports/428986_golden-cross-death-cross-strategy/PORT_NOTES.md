# #428986 Golden Cross Death Cross Strategy -> `fmz_428986_sma50_200_golden_cross`

- FMZ source id: 428986 (lineage).
- Source: https://www.fmz.com/strategy/428986 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 16:33:18). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [50, 20] x `length2` [200, 100]: **4 trials**.

## Ambiguities resolved

- Default SMA only. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
