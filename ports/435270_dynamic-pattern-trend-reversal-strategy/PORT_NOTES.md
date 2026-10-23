# #435270 Dynamic Pattern Trend Reversal Strategy -> `fmz_435270_volume_regression_prediction_wma_cross_macd_1m_reversal`

- FMZ source id: 435270 (lineage).
- Source: https://www.fmz.com/strategy/435270 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 16:52:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-regression price prediction crossings with a MACD filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): margin_long 100, margin_short 0, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435270. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `linear_len` [9, 20]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- rising / falling as earlier ports. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_regression"`.

## Marks

`none`
