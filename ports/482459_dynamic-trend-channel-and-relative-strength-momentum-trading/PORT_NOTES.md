# #482459 动态趋势通道与相对强弱指标相结合的量化交易策略-Dynamic-Trend-Channel-and-Relative-Strength-Momentum-Trading-Strategy -> `fmz_482459_keltner_reentry_rsi_extreme_mid_exit`

- FMZ source id: 482459 (lineage).
- Source: https://www.fmz.com/strategy/482459 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:15:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A Keltner channel and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [1.5, 2.5] x `rsi_len` [14, 7]: **4 trials**; defaults 1.5 / 14 (the source's); EMA 20, ATR 10 and the
70 / 30 levels fixed.

## Ambiguities resolved

- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
