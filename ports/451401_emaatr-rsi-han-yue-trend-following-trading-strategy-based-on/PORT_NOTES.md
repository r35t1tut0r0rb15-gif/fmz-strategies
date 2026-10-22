# #451401 漢越-基於多EMAATR和RSI的趨勢順勢交易策略-Han-Yue-Trend-Following-Trading-Strategy-Based-on-Multiple-EMAs-ATR-and-RSI -> `fmz_451401_two_candle_reversal_prior_extreme_stop_reversal`

- FMZ source id: 451401 (lineage).
- Source: https://www.fmz.com/strategy/451401 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-05-14 16:37:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-bar levels as fractions of the signal close |
| 2 | PASS | Two-candle reversal patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [1.5, 2.0]: **2 trials**; the patterns fixed.

## Ambiguities resolved

- Signal-bar levels as fractions of the signal close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
