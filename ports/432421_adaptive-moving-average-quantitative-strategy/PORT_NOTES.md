# #432421 Adaptive Moving Average Quantitative Strategy -> `fmz_432421_adaptive_touch_sma_turn`

- FMZ source id: 432421 (lineage).
- Source: https://www.fmz.com/strategy/432421 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-17 17:14:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Touches of an adaptive SMA and its slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10,000 USD cash per trade stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 10] x `smoothing` [3, 6]: **4 trials**; start length 20 and the 2-200 bounds fixed.

## Ambiguities resolved

- Adaptive length state as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
