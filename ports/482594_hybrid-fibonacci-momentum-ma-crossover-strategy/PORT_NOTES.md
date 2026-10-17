# #482594 混合型斐波那契动量均线交叉策略-Hybrid-Fibonacci-Momentum-MA-Crossover-Strategy -> `fmz_482594_sma9_21_cross_pct_bracket`

- FMZ source id: 482594 (lineage).
- Source: https://www.fmz.com/strategy/482594 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 11:02:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Two SMAs and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2, 4] x `tp_pct` [4, 8]: **4 trials**; defaults 2 / 4 (the source's); SMA 9 / 21 fixed.

## Ambiguities resolved

- Fibonacci levels and the trend label only feed drawings. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {}
  (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
