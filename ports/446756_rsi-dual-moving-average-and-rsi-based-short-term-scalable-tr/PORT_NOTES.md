# #446756 基于双均线和RSI的短线可扩展趋势追踪策略-Dual-Moving-Average-and-RSI-Based-Short-Term-Scalable-Trend-Following-Strategy -> `fmz_446756_sma5_10_contrarian_cross_rsi7_extreme_reversal`

- FMZ source id: 446756 (lineage).
- Source: https://www.fmz.com/strategy/446756 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-01 10:58:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Contrarian SMA crossings at RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `oversold` [20, 30]: **4 trials**; the SMAs and the overbought level fixed.

## Ambiguities resolved

- Closes on never-entered ids never act. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
