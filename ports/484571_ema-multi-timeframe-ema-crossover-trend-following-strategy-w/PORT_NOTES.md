# #484571 多重时框EMA交叉趋势跟踪策略结合支阻力与智能追踪止损系统-Multi-Timeframe-EMA-Crossover-Trend-Following-Strategy-with-Support-Resistance-and-Smart-Trailing-Stop-System -> `fmz_484571_ema5_cross_ema8_13_pct_trail_reversal`

- FMZ source id: 484571 (lineage).
- Source: https://www.fmz.com/strategy/484571 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 09:25:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | PASS | Triple EMA crossings with a percent trail |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_offset` [0.1, 0.01] x `ema_fast` [5, 3]: **4 trials**; EMA 8 / 13.

## Ambiguities resolved

- The trail input is used as a fraction (10 %), as written. The lookahead_on levels are plots only.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
