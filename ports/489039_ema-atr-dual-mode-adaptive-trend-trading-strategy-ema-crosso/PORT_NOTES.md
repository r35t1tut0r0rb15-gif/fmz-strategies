# #489039 双模式自适应趋势交易策略EMA交叉结合ATR波动率风险管理系统-Dual-Mode-Adaptive-Trend-Trading-Strategy-EMA-Crossover-with-ATR-Volatility-Based-Risk-Management-System -> `fmz_489039_adaptive_ema_cross_spaced_atr_bracket`

- FMZ source id: 489039 (lineage).
- Source: https://www.fmz.com/strategy/489039 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 14:20:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | EMAs, SMAs, RSI and ATR multiples. |
| 3 | PASS | "DOGE/USDT" in the title and the exchange pair only. |
| 4 | DONE | Leverage and the 1 %-risk quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trade_interval` [72, 5] x `use_adaptive` [True, False]: **4 trials**; defaults 72 / on (the source's); EMA 3 / 8 /
55, ATR 14, SL 1.2 / TP 2 ATR and the RSI strength 0.3 fixed.

## Ambiguities resolved

- The spacing is in bars, as written (the input's "minutes" label; 72 days on daily bars); the grid also tries 5.
- Entries only from flat: simulate() follows the house bracket on bars. A long wins over a short on one bar.
- Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
