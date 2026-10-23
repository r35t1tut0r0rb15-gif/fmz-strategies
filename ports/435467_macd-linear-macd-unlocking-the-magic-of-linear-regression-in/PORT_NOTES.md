# #435467 线性MACD解锁交易视图中线性回归的魔力Linear-MACD-Unlocking-the-Magic-of-Linear-Regression-in-TradingView -> `fmz_435467_obv_macd_volume_regression_prediction_1m_reversal`

- FMZ source id: 435467 (lineage).
- Source: https://www.fmz.com/strategy/435467 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 10:22:50). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | OBV MACD and volume-regression prediction filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): margin_long 100, margin_short 100, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `fast_len` [12, 8]: **4 trials**; slow 26, signal 9.

## Ambiguities resolved

- Same building blocks as #432241 / #435270. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_regression"`.

## Marks

`none`
