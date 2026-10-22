# #476273 Adaptive Trend Following Dynamic Trend Recognition Trading Strategy -> `fmz_476273_supertrend10x3_kama21_long`

- FMZ source id: 476273 (lineage).
- Source: https://www.fmz.com/strategy/476273 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 15:41:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend direction with a KAMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commission / slippage not ported; no sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kama_length` [21, 10] x `factor` [3.0, 2.0]: **4 trials**; ATR 10.

## Ambiguities resolved

- KAMA seeded from 0 as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
