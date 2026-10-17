# #487999 动态交叉移动平均线趋势捕捉策略与风险管理系统-Dynamic-Crossover-Moving-Average-Trend-Capture-Strategy-with-Risk-Management-System -> `fmz_487999_sma_cross_ema250_pct_trail`

- FMZ source id: 487999 (lineage).
- Source: https://www.fmz.com/strategy/487999 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 11:59:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop and trail from the fill (house trail). |
| 2 | PASS | Moving averages and percentages of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The leveraged quantity quoted; the stop and trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [0.0007, 0.0021] x `act_mult` [3.0, 6.0]: **4 trials**; defaults 0.0007 / 3 (the source's: 7 USD risk on
100 x 100 / close units is 0.07 % of the close; activation 3 x that); SMA 10 / 25 and EMA 250 fixed.

## Trailing stop (rule C1, mark `trailing_stop`)

`strategy.exit(stop = entry -+ dist, trail_points = 3 x dist, trail_offset = dist)` with dist = 0.07 % of the signal
close, price distances in tick arguments read as price distances (#427592). Ported natively as
`{"type": "percent", "pct": 0.0007, "activate_after": 0.0021, "anchor": "high_low"}` plus `sl_stop` 0.0007; the
house offset is a fraction of the best price (the source's a fixed price distance), equal to within 0.21 %.

## Ambiguities resolved

- The EMA 250 touch is bar-range-checked: an exit signal at the next open (#489638), from the position at the bar's
  start. Entries only from flat: `simulate()` mirrors the stop and trail on the port's bars from the fill bar (an
  approximation of the minute engine, #430254). Opposite entries cannot occur. Stop module: `portfolio_kwargs` {}
  (D4). FREQ = "2h": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop`
