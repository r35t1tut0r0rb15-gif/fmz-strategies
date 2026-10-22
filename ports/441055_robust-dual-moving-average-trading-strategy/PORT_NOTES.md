# #441055 Robust Dual Moving Average Trading Strategy -> `fmz_441055_rsi_roc_extreme_sma5_revert_above_sma200`

- FMZ source id: 441055 (lineage).
- Source: https://www.fmz.com/strategy/441055 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 10:57:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI, ROC and SMA levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND439860. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `trend_len` [200, 100]: **4 trials**; ROC 14, thresholds and the exit SMA 5 fixed.

## Ambiguities resolved

- Default block only (both sides, both oscillators, trend Above). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
