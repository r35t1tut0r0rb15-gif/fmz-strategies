# #482510 Dual EMA Adaptive Optimization Strategy with Dynamic Stop Management System -> `fmz_482510_ema5_10_cross_pct1_bracket_reversal`

- FMZ source id: 482510 (lineage).
- Source: https://www.fmz.com/strategy/482510 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 18:14:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | EMA crossings with a fixed percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_input` [1.0, 2.0] x `tp_input` [1.0, 3.0]: **4 trials**; EMA 5 / 10.

## Ambiguities resolved

- The netprofit "optimisation" never changes a level, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
