# #434691 Moving Average Crossover Strategy -> `fmz_434691_ema_7_20_cross_confirmed`

- FMZ source id: 434691 (lineage).
- Source: https://www.fmz.com/strategy/434691 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-08 12:20:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [7, 14] x `long_len` [20, 50]: **4 trials**.

## Ambiguities resolved

- Strict cross on the previous bar, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
