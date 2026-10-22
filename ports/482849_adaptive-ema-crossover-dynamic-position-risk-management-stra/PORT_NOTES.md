# #482849 Adaptive EMA Crossover Dynamic Position Risk Management Strategy -> `fmz_482849_ema21_55_cross_2bar_stop_2r_bracket_reversal`

- FMZ source id: 482849 (lineage).
- Source: https://www.fmz.com/strategy/482849 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:36:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 2-bar stop and 2R target as fractions of the fill |
| 2 | PASS | EMA crossings with a swing bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-percent quantity and 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mt_ema` [21, 9] x `rr` [2.0, 3.0]: **4 trials**; EMA 55, stop over 2 bars.

## Ambiguities resolved

- MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
