# #477569 Multi Indicator Probability Threshold Momentum Trend Trading Strategy -> `fmz_477569_rsi_stoch_macd_vote_zscore20_reversal`

- FMZ source id: 477569 (lineage).
- Source: https://www.fmz.com/strategy/477569 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 14:15:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator votes with a z-score filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `threshold` [0.5, 1.0]: **4 trials**; RSI 14, stochastic 14 / 3, MACD 12 / 26 / 9.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_momentum"`.

## Marks

`none`
