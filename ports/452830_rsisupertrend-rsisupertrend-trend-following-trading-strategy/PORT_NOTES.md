# #452830 RSISupertrend趋势跟踪交易策略-RSISupertrend-Trend-Following-Trading-Strategy -> `fmz_452830_rsi_supertrend_side_reversal`

- FMZ source id: 452830 (lineage).
- Source: https://www.fmz.com/strategy/452830 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 17:28:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels with the Supertrend side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_len` [10, 14] x `st_mult` [3.0, 2.0] x `rsi_len` [14, 7]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Date window dropped. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
