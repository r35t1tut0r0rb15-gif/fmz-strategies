# #477556 Dual Exponential Moving Average Momentum Crossover Trading Strategy -> `fmz_477556_smoothed_dema300_500_cross_flat_only`

- FMZ source id: 477556 (lineage).
- Source: https://www.fmz.com/strategy/477556 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 13:53:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the pip value input is unused. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [300, 50] x `long_len` [500, 200]: **4 trials**.

## Ambiguities resolved

- The stop levels are never sent. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
