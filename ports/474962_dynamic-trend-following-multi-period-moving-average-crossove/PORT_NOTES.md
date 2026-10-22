# #474962 Dynamic Trend Following Multi Period Moving Average Crossover Strategy -> `fmz_474962_sma21_89_trend_ema5_pullback_point_bracket_reversal`

- FMZ source id: 474962 (lineage).
- Source: https://www.fmz.com/strategy/474962 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:40:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fixed fractions of the fill |
| 2 | PASS | Trend pullbacks with a point bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Contract count stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.000595, 0.00595] x `tp_frac` [0.000595, 0.00595]: **4 trials**; the averages fixed.

## Ambiguities resolved

- Only the first id fills (pyramiding 1). Points as fractions of 42000. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`
