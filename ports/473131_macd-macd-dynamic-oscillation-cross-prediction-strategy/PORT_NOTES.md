# #473131 MACD动态波动交叉预测策略-MACD-Dynamic-Oscillation-Cross-Prediction-Strategy -> `fmz_473131_macd_hist_anticipated_cross_long`

- FMZ source id: 473131 (lineage).
- Source: https://www.fmz.com/strategy/473131 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:54:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram turns before the zero cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21] x `signal` [2, 9]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
