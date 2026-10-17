# #489152 移动平均线交叉与动态波动率止损量化策略-Moving-Average-Crossover-with-Dynamic-Volatility-Based-Stop-Loss-Strategy -> `fmz_489152_sma_50_below_200_rsi_atr_bracket_long`

- FMZ source id: 489152 (lineage).
- Source: https://www.fmz.com/strategy/489152 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:08:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | SMAs, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.0, 2.0] x `rr` [1.5, 3.0]: **4 trials**; defaults 1 / 1.5 (the source's); SMA 50 / 200, RSI 14 and
ATR 14 fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

The exit is re-issued every bar at the fill +- the current ATR multiples, so the levels move with the ATR. Fixed at
the signal bar's ATR here.

## Ambiguities resolved

- The long condition is SMA 50 below SMA 200, as written. Every condition bar is an entry. Long only.
- Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
