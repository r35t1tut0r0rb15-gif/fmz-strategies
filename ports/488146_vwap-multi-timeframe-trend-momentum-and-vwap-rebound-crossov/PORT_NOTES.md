# #488146 多时间框架趋势动量与VWAP反弹交叉量化策略-Multi-Timeframe-Trend-Momentum-and-VWAP-Rebound-Crossover-Quantitative-Strategy -> `fmz_488146_ema_cross_vwap_bounce_window_trail_pending_1h_reversal`

- FMZ source id: 488146 (lineage).
- Source: https://www.fmz.com/strategy/488146 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 14:25:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trailing exit pending |
| 2 | PASS | EMA crossings and VWAP bounces in a low-volatility window |
| 3 | PASS | Exchange pair in the header only (HDFC Bank named in the title). |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_pct` [1.0, 2.0] x `fast` [9, 12]: **4 trials**; EMA 21, RSI 14, window 10-13 UTC.

## Ambiguities resolved

- Trailing exit pending (not expressible); window on UTC. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`trailing_stop_pending`
