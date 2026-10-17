# #484571 多重时框EMA交叉趋势跟踪策略结合支阻力与智能追踪止损系统-Multi-Timeframe-EMA-Crossover-Trend-Following-Strategy-with-Support-Resistance-and-Smart-Trailing-Stop-System -> `fmz_484571_ema5_double_cross_pct_trail`

- FMZ source id: 484571 (lineage).
- Source: https://www.fmz.com/strategy/484571 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 09:25:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; trail from the fill (house trail). |
| 2 | PASS | EMAs and a percentage trail. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_frac` [0.10, 0.001] x `slow` [13, 21]: **4 trials**; defaults 0.10 / 13 (the source as written: the "%" input
0.10 is used as a fraction, a 10 % trail; 0.001 is the label's 0.1 % reading); EMA 5 / 8 fixed.

## Trailing stop (rule C1, mark `trailing_stop`)

As written: from the fill bar, `maxHigh` = highest high since entry, `longStop = max(longStop, maxHigh x (1 - 0.10))`,
`strategy.exit(stop = longStop)` (shorts mirrored with the lowest low). Ported natively as
`{"type": "percent", "pct": 0.10, "anchor": "high_low"}` (best minute high up to the previous minute: the same
granularity on 1-minute bars).

## Ambiguities resolved

- The hourly S/R values (`lookahead_on` with `[1]`, the previous hour) feed plots only. The close after each entry
  is the reversal: REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
