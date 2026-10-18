# #435698 基于布林带和-StochRSI-指标的高频交易策略High-Frequency-Trading-Strategy-Based-on-Bollinger-Bands-and-StochRSI-Indicators -> `fmz_435698_lower_bollinger_long_hold`

- FMZ source id: 435698 (lineage).
- Source: https://www.fmz.com/strategy/435698 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 10:16:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band |
| 3 | PASS |  |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `dev` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- No exit in the script: long held. Long only. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`bar_size_pending`
