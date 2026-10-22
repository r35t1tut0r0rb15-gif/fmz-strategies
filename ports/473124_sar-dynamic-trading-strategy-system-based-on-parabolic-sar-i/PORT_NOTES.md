# #473124 基于抛物线SAR指标的动态交易策略系统-Dynamic-Trading-Strategy-System-Based-on-Parabolic-SAR-Indicator -> `fmz_473124_parabolic_sar_flip_reversal`

- FMZ source id: 473124 (lineage).
- Source: https://www.fmz.com/strategy/473124 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:23:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Parabolic SAR flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [0.02, 0.01] x `maximum` [0.2, 0.1]: **4 trials**; the increment equals the start.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
