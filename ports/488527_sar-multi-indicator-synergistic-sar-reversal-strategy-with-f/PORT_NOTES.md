# #488527 多指标联动SAR反转策略与过滤入场模型-Multi-Indicator-Synergistic-SAR-Reversal-Strategy-with-Filtered-Entry-Model -> `fmz_488527_psar_cross_rsi_macd_stochrsi_lsma_filter_reversal`

- FMZ source id: 488527 (lineage).
- Source: https://www.fmz.com/strategy/488527 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 16:36:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR crossings with RSI / MACD / Stochastic RSI / LSMA filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lsmaOffset` [9, 0] x `stochLength` [14, 7]: **4 trials**; SAR 0.02 / 0.02 / 0.2, RSI 14, LSMA 4.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
