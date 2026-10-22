# #474834 增强型趋势跟踪策略基于ADX与抛物线SAR的动态趋势识别系统-Enhanced-Trend-Following-System-Dynamic-Trend-Identification-Based-on-ADX-and-Parabolic-SAR -> `fmz_474834_adx25_di_sar_trend_state_reversal`

- FMZ source id: 474834 (lineage).
- Source: https://www.fmz.com/strategy/474834 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 14:21:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX / DI trend states with a SAR filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25, 20] x `adx_len` [14, 20]: **4 trials**; SAR settings fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
