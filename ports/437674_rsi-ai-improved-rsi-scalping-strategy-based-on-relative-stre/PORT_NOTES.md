# #437674 基于RSI和AI自定义条件进行交易的高级策略Improved-RSI-Scalping-Strategy-based-on-Relative-Strength-Index -> `fmz_437674_rsi_cross_follow_up`

- FMZ source id: 437674 (lineage).
- Source: https://www.fmz.com/strategy/437674 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-04 17:20:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | RSI crossings; the every-bar tick bracket is pending |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk size formula, fixed quantity and the tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `oversold` [30.0, 20.0]: **4 trials**; overbought = 100 - oversold; the bracket is pending.

## Ambiguities resolved

- First-bar var conditions as written; every-bar tick bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
