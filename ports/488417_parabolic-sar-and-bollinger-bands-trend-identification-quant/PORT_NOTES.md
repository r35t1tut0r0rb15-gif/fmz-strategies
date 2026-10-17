# #488417 抛物线停损反转与布林带趋势识别量化交易策略-Parabolic-SAR-and-Bollinger-Bands-Trend-Identification-Quantitative-Trading-Strategy -> `fmz_488417_sar_side_inside_bollinger`

- FMZ source id: 488417 (lineage).
- Source: https://www.fmz.com/strategy/488417 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-27 14:20:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | SAR and bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_max` [0.2, 0.1] x `bb_mult` [2.0, 2.5]: **4 trials**; defaults 0.2 / 2 (the source's); SAR start 0.02 and BB 20
fixed; the SAR increment equals `sar_max`, as written.

## Ambiguities resolved

- `ta.sar(sar_step, sar_max, sar_max)`: the increment is the maximum, as written (#428699 algorithm).
- Closes act on the position held at the bar's start (#430850); a signal against the position reverses it.
  REVERSAL INTENDED. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
