# #428969 Double Hull Moving Average Crossover Trading Strategy -> `fmz_428969_hull_60_175_cross`

- FMZ source id: 428969 (lineage).
- Source: https://www.fmz.com/strategy/428969 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 14:49:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [60, 30] x `alength` [175, 100]: **4 trials**.

## Ambiguities resolved

- Integer half-lengths. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
