# #445804 Candlestick Pattern Trend Filter Strategy -> `fmz_445804_engulfing_sma14_60_trend_reversal`

- FMZ source id: 445804 (lineage).
- Source: https://www.fmz.com/strategy/445804 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 14:01:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Engulfing patterns with trend filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 5 % of equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 20] x `slow` [60, 100]: **4 trials**.

## Ambiguities resolved

- Morning-star and dark-cloud branches never fire, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
