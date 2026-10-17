# #489650 动态波动率自适应EMAxRSI交叉策略-Dynamic-Volatility-Adaptive-EMA-RSI-Crossover-Strategy -> `fmz_489650_ema_20_50_cross_rsi_atr_bracket`

- FMZ source id: 489650 (lineage).
- Source: https://www.fmz.com/strategy/489650 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 13:25:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | EMAs, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1 %-risk lot quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.0, 2.0] x `tp_atr` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 20 / 50, RSI 14
(70 / 30) and ATR 14 fixed.

## Ambiguities resolved

- Closes before entries: stop-and-reverse. REVERSAL INTENDED.
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
