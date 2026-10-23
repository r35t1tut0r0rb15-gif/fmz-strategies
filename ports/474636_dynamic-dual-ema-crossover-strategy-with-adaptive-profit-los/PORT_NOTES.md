# #474636 Dynamic Dual EMA Crossover Strategy with Adaptive Profit Loss Control -> `fmz_474636_ema20_50_cross_up_130_95pct_bracket_long_only`

- FMZ source id: 474636 (lineage).
- Source: https://www.fmz.com/strategy/474636 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 11:23:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA 20 / 50 cross-ups |
| 3 | PASS | Exchange pair in the header only (TQQQ named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [1.3, 1.15] x `sl_mult` [0.95, 0.9]: **4 trials**; EMA 20 / 50.

## Ambiguities resolved

- One long at a time; bracket at the signal close. Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
