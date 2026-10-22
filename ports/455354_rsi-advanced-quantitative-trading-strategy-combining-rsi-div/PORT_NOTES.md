# #455354 高级RSI背离与均线组合的量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-RSI-Divergence-and-Moving-Averages -> `fmz_455354_rsi60_pivot_divergence_reversal`

- FMZ source id: 455354 (lineage).
- Source: https://www.fmz.com/strategy/455354 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:02:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket pending (mark) |
| 2 | PASS | Regular RSI divergences at pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the pip bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [60, 14] x `pivot` [5, 3]: **4 trials**; the 5-60 range and the 40 / 60 levels fixed.

## Ambiguities resolved

- Late-armed bracket pending; reversal exits only. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
