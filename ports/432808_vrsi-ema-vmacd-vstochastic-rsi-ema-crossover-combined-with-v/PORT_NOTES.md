# #432808 VRSI-EMA交叉与VMACD融合的波浪寻找者策略VSTOCHASTIC-RSI-EMA-CROSSOVER-COMBINED-WITH-VMACD-WAVEFINDER-STRATEGY -> `fmz_432808_stoch_rsi_vwmacd_wavefinder_long`

- FMZ source id: 432808 (lineage).
- Source: https://www.fmz.com/strategy/432808 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-21 17:12:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI and volume-weighted MACD long setups |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 10000 / close, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `confirm_bars` [2, 3]: **4 trials**; VWMACD 12 / 26 / 9, stochastic RSI 14 / 14 / 3 / 3.

## Ambiguities resolved

- bcount == 2 exactly, as written. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_rsi"`.

## Marks

`none`
