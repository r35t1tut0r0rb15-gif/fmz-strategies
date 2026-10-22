# #482451 基于高斯通道与随机RSI的量化交易策略优化系统-Gaussian-Channel-with-Stochastic-RSI-Quantitative-Trading-Strategy-Optimization-System -> `fmz_482451_ema20_sd_channel_reentry_stochrsi_long`

- FMZ source id: 482451 (lineage).
- Source: https://www.fmz.com/strategy/482451 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:00:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel re-entries with Stochastic RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity and capital stored, not ported; commission not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gc_length` [20, 50] x `gc_mult` [2.0, 1.5]: **4 trials**; Stoch RSI 14 / 14 / 3, 20 / 80.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
