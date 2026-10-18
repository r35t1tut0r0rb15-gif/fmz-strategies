# #436145 双MA交叉趋势追踪策略Dual-MA-Crossover-Trend-Tracking-Strategy -> `fmz_436145_ema_open_state_change_bracket`

- FMZ source id: 436145 (lineage).
- Source: https://www.fmz.com/strategy/436145 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-21 16:10:22). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick amounts -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`invert` [False, True] x `k_atr` [0.07, 1.0]: **4 trials**; EMA 14 / 21 of the open fixed; the target is 5 x the stop.

## Ambiguities resolved

- Tick amounts -> ATR multiples; trail without offset inactive. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
