# #474880 多指标协同布林带-斐波那契-MACD-RSI智能交易策略-Multi-Indicator-Synergistic-Trading-Strategy-with-Bollinger-Bands-Fibonacci-MACD-and-RSI -> `fmz_474880_bb_fib_macd_rsi_any_signal_max_price_exit_reversal`

- FMZ source id: 474880 (lineage).
- Source: https://www.fmz.com/strategy/474880 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 17:20:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; conditional exit orders read as next-open closes |
| 2 | PASS | Any-of-four signals with a max-price exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback_fib` [50, 100] x `sl_pct` [0.02, 0.04]: **4 trials**; take profit 5 %, BB / MACD / RSI fixed.

## Ambiguities resolved

- Conditional exits read as next-open closes; the max price never resets; shorts last one bar, as written. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
