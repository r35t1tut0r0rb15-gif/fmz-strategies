# #435487 多种K线形态综合策略Comprehensive-Strategy-of-Multiple-Candlestick-Patterns -> `fmz_435487_candlestick_pattern_library`

- FMZ source id: 435487 (lineage).
- Source: https://www.fmz.com/strategy/435487 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 12:03:17). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Candle patterns and percent stops on closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial capital input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss` [0.015, 0.03] x `sma_len` [50, 100]: **4 trials**; body average 14 and the pattern thresholds fixed.

## Ambiguities resolved

- Persistent direction while flat; sequential order fills; pattern switches at their defaults. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
