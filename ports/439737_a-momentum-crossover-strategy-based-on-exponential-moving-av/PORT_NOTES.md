# #439737 A Momentum Crossover Strategy Based on Exponential Moving Average -> `fmz_439737_pierce_ema10_20_cross_run_gate`

- FMZ source id: 439737 (lineage).
- Source: https://www.fmz.com/strategy/439737 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-23 14:18:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and run counts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [10, 5] x `len2` [20, 30]: **4 trials**; run limits 10 / 5 and the 3-bar gap fixed.

## Ambiguities resolved

- Run-length reading of the barssince chain. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
