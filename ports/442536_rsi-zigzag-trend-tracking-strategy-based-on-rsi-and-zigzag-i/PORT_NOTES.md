# #442536 基于RSI指标和ZigZag指标趋势追踪策略Trend-Tracking-Strategy-Based-on-RSI-and-ZigZag-Indicators -> `fmz_442536_rsi_cross_close_zigzag_long`

- FMZ source id: 442536 (lineage).
- Source: https://www.fmz.com/strategy/442536 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 16:15:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zigzag on RSI-cross closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND379760. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 14] x `zz_pct` [1.0, 2.0]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- Zigzag state as written (zero starts). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
