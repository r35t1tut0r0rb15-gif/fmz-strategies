# #485283 RSI反转斐波那契布林带量化策略-RSI-Reversal-Fibonacci-Bollinger-Bands-Quantitative-Strategy -> `fmz_485283_rsi14_into_30_70_zone_reversal`

- FMZ source id: 485283 (lineage).
- Source: https://www.fmz.com/strategy/485283 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-20 11:42:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent close bracket pending |
| 2 | PASS | RSI zone entries |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_os` [30, 20] x `rsi_length` [14, 7]: **4 trials**; overbought 100 - oversold.

## Ambiguities resolved

- The per-bar bracket is pending, not ported; the VWMA bands are plots only. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
