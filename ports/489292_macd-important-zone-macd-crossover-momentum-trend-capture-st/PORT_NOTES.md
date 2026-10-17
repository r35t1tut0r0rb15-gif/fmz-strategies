# #489292 重要区间MACD交叉动量趋势捕捉策略-Important-Zone-MACD-Crossover-Momentum-Trend-Capture-Strategy -> `fmz_489292_macd_cross_zero_zone`

- FMZ source id: 489292 (lineage).
- Source: https://www.fmz.com/strategy/489292 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:59:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | The +-0.5 price-unit zone -> +-`zone_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone_atr` [0.125, 0.5] x `slow` [26, 50]: **4 trials**; defaults 0.125 / 26; fast 12 and signal 9 fixed. On hourly
BNB_USDT 0.5 is about 0.125 ATR (judgement, stated before any backtest).

## Ambiguities resolved

- The closes act on the position held at the bar's start; a cross outside the zone only closes.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
