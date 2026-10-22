# #446558 RSI-动量策略-RSI-Momentum-Strategy-with-Manual-TP-and-SL -> `fmz_446558_rsi_30_70_recovery_range_filter_1pct_bracket_reversal`

- FMZ source id: 446558 (lineage).
- Source: https://www.fmz.com/strategy/446558 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:35:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | RSI threshold recoveries with a range filter, percent bracket |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `bracket` [0.01, 0.02]: **4 trials**; the RSI levels and the range filter fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); bracket 1 % of the fill. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`bar_size_pending`
