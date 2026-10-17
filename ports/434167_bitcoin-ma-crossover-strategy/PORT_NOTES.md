# #434167 Bitcoin MA Crossover Strategy -> `fmz_434167_sma_cross_rsi_filter`

- FMZ source id: 434167 (lineage).
- Source: https://www.fmz.com/strategy/434167 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-04 13:55:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crosses and an RSI side filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-risk unit count stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [40, 80]: **4 trials**; RSI 14 / 50 fixed.

## Ambiguities resolved

- Opposite-size orders read as closes. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
