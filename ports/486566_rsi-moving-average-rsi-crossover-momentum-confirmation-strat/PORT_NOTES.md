# #486566 滑动平均-RSI-交叉动量确认策略-Moving-Average-RSI-Crossover-Momentum-Confirmation-Strategy -> `fmz_486566_sma20_30_cross_rsi_tp`

- FMZ source id: 486566 (lineage).
- Source: https://www.fmz.com/strategy/486566 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-14 09:35:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a close-checked target. |
| 2 | PASS | Moving averages, an oscillator and a percentage. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [2.0, 4.0] x `sma_long` [30, 50]: **4 trials**; defaults 2 / 30 (the source's); SMA 20 and RSI 14 (25 / 75)
fixed; the full-position take profit on.

## Ambiguities resolved

- `inBuyState` stays on after a take-profit close and `entryPrice` moves with every buy signal, as written; the
  target is close-checked (rule 3). Closes act on the position at the bar's start (#430850). The half-position
  option (a partial exit) is off by default: not ported. Long only: opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
