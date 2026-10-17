# #482489 双均线趋势交叉结合ADX动量过滤的自适应风险策略-Adaptive-Risk-Strategy-with-Dual-EMA-Crossover-and-ADX-Momentum-Filter -> `fmz_482489_ema50_200_adx_ema50_cross_swing_atr_bracket`

- FMZ source id: 482489 (lineage).
- Source: https://www.fmz.com/strategy/482489 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 16:21:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | EMAs, DMI / ADX, swing extremes and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25, 20] x `rr` [1.5, 2.5]: **4 trials**; defaults 25 / 1.5 (the source's); EMA 50 / 200, DMI 14, swing 5
and the 0.5 ATR buffer fixed.

## Ambiguities resolved

- The title says XAUUSD 15m; the backtest header's 3-minute bars are used.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
