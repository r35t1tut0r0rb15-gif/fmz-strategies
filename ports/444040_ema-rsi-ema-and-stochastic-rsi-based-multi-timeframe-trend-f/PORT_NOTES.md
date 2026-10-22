# #444040 基于EMA和随机RSI的多周期趋势跟踪交易策略EMA-and-Stochastic-RSI-based-Multi-timeframe-Trend-Following-Trading-Strategy -> `fmz_444040_xo_ema12_25_first_bar_flip_reversal`

- FMZ source id: 444040 (lineage).
- Source: https://www.fmz.com/strategy/444040 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 17:32:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA order flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 9] x `slow` [25, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
