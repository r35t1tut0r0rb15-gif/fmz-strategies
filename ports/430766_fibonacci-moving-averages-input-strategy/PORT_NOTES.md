# #430766 Fibonacci Moving Averages Input Strategy -> `fmz_430766_fib_ma_crosses`

- FMZ source id: 430766 (lineage).
- Source: https://www.fmz.com/strategy/430766 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-01 16:42:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_len` [34, 21] x `cross_len` [144, 89]: **4 trials**; the short pair (55 over the SMA of the same cross length) follows.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
