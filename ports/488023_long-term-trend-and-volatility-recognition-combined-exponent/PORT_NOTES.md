# #488023 Long term Trend and Volatility Recognition Combined Exponential Moving Average SuperTrend Quantitative Trading Strategy -> `fmz_488023_handbuilt_supertrend3_14_sma200_side_reversal`

- FMZ source id: 488023 (lineage).
- Source: https://www.fmz.com/strategy/488023 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:42:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend states with an SMA side filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `ma_length` [200, 100]: **4 trials**; ATR 14.

## Ambiguities resolved

- The hand-built trend rule is as written. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
