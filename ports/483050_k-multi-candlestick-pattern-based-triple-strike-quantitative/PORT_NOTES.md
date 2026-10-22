# #483050 基于多重K线形态的三重打击量化交易策略-Multi-Candlestick-Pattern-Based-Triple-Strike-Quantitative-Trading-Strategy -> `fmz_483050_three_line_strike_reversal`

- FMZ source id: 483050 (lineage).
- Source: https://www.fmz.com/strategy/483050 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:12:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three-line-strike candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

GRID = {}: No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- The default-off engulfing entries are not ported. REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
