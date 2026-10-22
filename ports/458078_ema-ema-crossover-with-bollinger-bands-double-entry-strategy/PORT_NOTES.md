# #458078 EMA交叉与布林带双重入场策略结合趋势跟踪与波动突破的量化交易系统EMA-Crossover-with-Bollinger-Bands-Double-Entry-Strategy-A-Quantitative-Trading-System-Combining-Trend-Following-and-Volatility-Breakout -> `fmz_458078_ema12_26_cross_bb_breakout_atr_stop_reentry_long`

- FMZ source id: 458078 (lineage).
- Source: https://www.fmz.com/strategy/458078 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:14:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fixed stop level as a fraction of the fill |
| 2 | PASS | EMA crossings and band breakouts with an ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity-risk position sizes stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 9] x `slow` [26, 21] x `atr_mult` [1.0, 2.0]: **8 trials**; the bands fixed.

## Ambiguities resolved

- Stop taken from the fill bar (source: the bar after); marketable stop sent as a next-open exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
