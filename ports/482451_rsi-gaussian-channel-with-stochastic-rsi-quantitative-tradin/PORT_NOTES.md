# #482451 基于高斯通道与随机RSI的量化交易策略优化系统-Gaussian-Channel-with-Stochastic-RSI-Quantitative-Trading-Strategy-Optimization-System -> `fmz_482451_ema_stdev_channel_stoch_rsi_cross_long`

- FMZ source id: 482451 (lineage).
- Source: https://www.fmz.com/strategy/482451 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:00:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An EMA-stdev channel and a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity; the commission is a cost. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gc_mult` [2.0, 1.5] x `gc_length` [20, 40]: **4 trials**; defaults 2 / 20 (the source's); RSI 14, stochastic 14 /
3 and the 80 / 20 levels fixed.

## Ambiguities resolved

- The "Gaussian" channel is an EMA with a stdev band (as written).
- Clock rule (check 9 / C6): the 2018-2069 window read as UTC.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
