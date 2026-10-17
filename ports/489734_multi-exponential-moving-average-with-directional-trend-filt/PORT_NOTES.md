# #489734 多指数移动平均与方向性趋势过滤交易系统-Multi-Exponential-Moving-Average-with-Directional-Trend-Filter-Trading-System -> `fmz_489734_ema_5_8_cross_ema13_exit`

- FMZ source id: 489734 (lineage).
- Source: https://www.fmz.com/strategy/489734 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-08 10:13:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs and ADX |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted (the commission is a cost). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_adx` [False, True] x `exit_ema` [13, 21]: **4 trials**; defaults off / 13 (the source's); EMA 5 / 8 and the ADX
threshold 20 fixed.

## Ambiguities resolved

- The EMA 13 closes act on the position held at the bar's start. The ADX filter is the source's own switch.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
