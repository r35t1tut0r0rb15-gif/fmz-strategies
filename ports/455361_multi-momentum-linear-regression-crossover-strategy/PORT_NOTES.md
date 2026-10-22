# #455361 Multi Momentum Linear Regression Crossover Strategy -> `fmz_455361_ema5_20_cross_rsi50_reversal`

- FMZ source id: 455361 (lineage).
- Source: https://www.fmz.com/strategy/455361 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:21:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [20, 50] x `rsi_len` [14, 7]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
