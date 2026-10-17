# #489309 道氏理论趋势自适应动量策略Dow-Theory-Trend-Adaptive-Momentum-Strategy -> `fmz_489309_dow_pivot_trend_change_bracket`

- FMZ source id: 489309 (lineage).
- Source: https://www.fmz.com/strategy/489309 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 13:05:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed after their right bars. |
| 2 | ADAPT | 100 / 200 ticks -> `sl_atr` x ATR(14) and 2 x that. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot` [10, 5] x `sl_atr` [1.5, 3.0]: **4 trials**; defaults 10 / 1.5; target ratio 2 fixed. On 2-minute BNB_USDT
100 ticks of 0.01 are about 0.17 %, about 1.5 ATR (judgement, stated before any backtest).

## Ambiguities resolved

- Pivots strict, confirmed 10 bars later; a pivot equal to the stored one is not stored, as written.
- `loss` / `profit` are distances from the fill, as the house stops. REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
