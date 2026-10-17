# #482836 基于动态ATR和双均线交叉的自适应风险管理策略-Adaptive-Risk-Management-Strategy-Based-on-Dynamic-ATR-and-Moving-Average-Crossover -> `fmz_482836_sma10_100_cross_cooldown_atr_rr`

- FMZ source id: 482836 (lineage).
- Source: https://www.fmz.com/strategy/482836 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:07:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Two SMAs and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity and the 1 % risk input quoted; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `rr` [2.0, 3.0]: **4 trials**; defaults 1.5 / 2 (the source's); SMA 10 / 100, cooldown 10
and ATR 14 fixed.

## Ambiguities resolved

- Clock rule (check 9 / C6): the trading window is 00:00-23:59 UTC on each bar's opening time. Every two-hour bar
  opens inside it, so the filter and the `strategy.close(..., when = not isTimeValid)` calls never act (no-op).
- The cooldown counts bars since the last signal taken (whatever the position).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
