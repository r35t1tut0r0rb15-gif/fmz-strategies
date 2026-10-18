# #435871 Directional Movement Index Dual direction Trading Strategy -> `fmz_435871_noro_di_dominance`

- FMZ source id: 435871 (lineage).
- Source: https://www.fmz.com/strategy/435871 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 14:13:52). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Directional movement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot, capital percent and pyramiding inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [14, 20] x `limit` [3, 5]: **4 trials**.

## Ambiguities resolved

- Running-sum smoothing; start from zero. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
