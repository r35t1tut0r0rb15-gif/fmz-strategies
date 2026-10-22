# #458254 Triple EMA with Dynamic Support Resistance Trading Strategy -> `fmz_458254_ema10_20_cross_ema50_close_extreme_filter_pct_bracket_reversal`

- FMZ source id: 458254 (lineage).
- Source: https://www.fmz.com/strategy/458254 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:58:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | EMA crossings with trend and level filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 5] x `mid_len` [20, 30] x `sl_pct` [0.01, 0.03]: **8 trials**; the 2 % target and EMA 50 fixed.

## Ambiguities resolved

- Bracket as fractions of the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
