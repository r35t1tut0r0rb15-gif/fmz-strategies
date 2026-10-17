# #489311 动态趋势识别策略与指数移动平均线和自适应波动阈值-Dynamic-Trend-Identification-Strategy-with-Exponential-Moving-Average-and-Adaptive-Volatility-Threshold -> `fmz_489311_onetrend_lite_ema_gap_long`

- FMZ source id: 489311 (lineage).
- Source: https://www.fmz.com/strategy/489311 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 13:08:04). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An EMA gap in ATR units and ADX |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG489311 (2 members, best partner #490075, Jaccard 1.000; not an exact duplicate). |
| 7 | IGNORED | The performance tables in the comments are ignored. |

## Declared grid (criterion 5)

`ema_fast` [30, 20] x `atr_mult_strong` [0.3, 0.6]: **4 trials**; defaults 30 / 0.3 (the source's); EMA 60, ATR 60,
ADX 14 (20) and the weak multiple 0.1 fixed.

## Ambiguities resolved

- The source's own DMI (DM 0 where the change is na; dx na where the DI sum is 0).
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
