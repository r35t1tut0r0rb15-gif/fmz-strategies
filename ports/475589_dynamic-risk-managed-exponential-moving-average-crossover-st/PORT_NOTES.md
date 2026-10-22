# #475589 Dynamic Risk Managed Exponential Moving Average Crossover Strategy -> `fmz_475589_ema9_21_cross_1_2pct_bracket_long`

- FMZ source id: 475589 (lineage).
- Source: https://www.fmz.com/strategy/475589 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:08:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a bracket and a cross-down exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size from equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; risk 1 %, reward 2.

## Ambiguities resolved

- No trail (offset only). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
