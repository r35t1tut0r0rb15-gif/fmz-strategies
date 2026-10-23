# #428617 Multi indicator Combination Strategy -> `fmz_428617_fourteen_part_point_score_zero_cross_reversal`

- FMZ source id: 428617 (lineage).
- Source: https://www.fmz.com/strategy/428617 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 15:34:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Multi-indicator point score zero crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000, commission 0.075 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_mult` [3.0, 2.0] x `sma_len` [20, 50]: **4 trials**; the other parts as written.

## Ambiguities resolved

- Every part as written (na sides included). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
