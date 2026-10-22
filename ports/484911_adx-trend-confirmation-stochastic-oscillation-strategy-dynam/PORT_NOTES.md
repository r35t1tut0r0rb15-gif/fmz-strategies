# #484911 趋势确认随机震荡策略ADX与随机指标结合的动态市场识别系统-Trend-Confirmation-Stochastic-Oscillation-Strategy-Dynamic-Market-Identification-System-Combining-ADX-and-Stochastic-Indicators -> `fmz_484911_stoch14_kd_cross_extremes_adx25_long`

- FMZ source id: 484911 (lineage).
- Source: https://www.fmz.com/strategy/484911 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-05 09:42:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic extreme crossings with an ADX filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25.0, 20.0] x `stoch_k_period` [14, 9]: **4 trials**; ADX 14, smooth 3, D 3, levels 80 / 20.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
