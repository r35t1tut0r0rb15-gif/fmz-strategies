# #471720 Multi Level Moving Average with Candlestick Pattern Recognition Trading System -> `fmz_471720_twenty_candle_patterns_ema6_reversal`

- FMZ source id: 471720 (lineage).
- Source: https://www.fmz.com/strategy/471720 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:39:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candlestick patterns against an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_input` [6, 20]: **2 trials**; the pattern ratios fixed.

## Ambiguities resolved

- Exact-equality patterns as written; later call wins on mixed bars. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
