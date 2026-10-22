# #478707 Multi EMA Trend Following Strategy with Dynamic Volatility Filter -> `fmz_478707_three_candle_growth_range_filter_ema50_reversal`

- FMZ source id: 478707 (lineage).
- Source: https://www.fmz.com/strategy/478707 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 15:00:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three-candle momentum patterns with a range and trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`filter_number` [1.5, 1.0] x `ema_trend` [50, 100]: **4 trials**.

## Ambiguities resolved

- The TP / SL labels send no orders. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
