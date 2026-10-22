# #443988 The EMA Cross Quantitative Strategy -> `fmz_443988_ema200_trend_ema10_exit_fill_stop_long`

- FMZ source id: 443988 (lineage).
- Source: https://www.fmz.com/strategy/443988 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 14:18:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend entry with an EMA 10 and fill-price exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438794. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [200, 100] x `ma2` [10, 20]: **4 trials**; the stop fixed.

## Ambiguities resolved

- Fill-price stop at the close. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
