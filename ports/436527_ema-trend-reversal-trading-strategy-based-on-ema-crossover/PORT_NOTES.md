# #436527 基于EMA交叉的趋势转向交易策略Trend-Reversal-Trading-Strategy-Based-on-EMA-Crossover -> `fmz_436527_ema_cross_rsi_gate`

- FMZ source id: 436527 (lineage).
- Source: https://www.fmz.com/strategy/436527 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-25 15:12:46). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C91). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Crossings gated by an RSI side test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [50, 100]: **4 trials**; RSI 14 with 70 / 30 fixed.

## Ambiguities resolved

- is_trending is redundant for crossings. Orders in call order. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
