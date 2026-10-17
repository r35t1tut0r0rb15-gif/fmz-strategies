# #484911 趋势确认随机震荡策略ADX与随机指标结合的动态市场识别系统-Trend-Confirmation-Stochastic-Oscillation-Strategy-Dynamic-Market-Identification-System-Combining-ADX-and-Stochastic-Indicators -> `fmz_484911_adx_stoch_extreme_cross_long`

- FMZ source id: 484911 (lineage).
- Source: https://www.fmz.com/strategy/484911 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-05 09:42:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ADX and a stochastic. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25.0, 20.0] x `band` [20, 30]: **4 trials**; defaults 25 / 20 (the source's; the upper level is
100 - band, 80 by default); ADX 14 and stochastic 14 / 3 / 3 fixed.

## Ambiguities resolved

- The DMI as written (the first true range is na because close[1] is). Long only, exit on the opposite
  extreme cross: opposite entries cannot occur. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
