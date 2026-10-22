# #440983 基于EMA和RSI的强大量化交易策略Powerful-EMA-and-RSI-Quantitative-Trading-Strategy -> `fmz_440983_ema50_side_rsi_strength`

- FMZ source id: 440983 (lineage).
- Source: https://www.fmz.com/strategy/440983 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 15:12:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA side and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `rsi_hi` [55, 60]: **4 trials**; the low level = 100 - high.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
