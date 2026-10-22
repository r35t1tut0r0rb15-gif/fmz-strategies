# #458063 多重EMA交叉结合斐波那契扩展的趋势跟踪策略-Multi-EMA-Crossover-with-Fibonacci-Extension-Trend-Following-Strategy -> `fmz_458063_ema5_10_30_setups_fib_extension_exits_long`

- FMZ source id: 458063 (lineage).
- Source: https://www.fmz.com/strategy/458063 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:42:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stops and targets are close tests |
| 2 | PASS | EMA set-ups with set-up stops and Fibonacci targets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing_len` [20, 50]: **2 trials**; the EMA lengths and the set-ups fixed.

## Ambiguities resolved

- Flags and position followed separately. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
