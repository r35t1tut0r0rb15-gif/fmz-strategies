# #482473 基于价格结构的高比例回报突破交易策略-High-Reward-to-Risk-Price-Structure-Breakout-Trading-Strategy -> `fmz_482473_prior_extreme_cross_swing_stop_rr5`

- FMZ source id: 482473 (lineage).
- Source: https://www.fmz.com/strategy/482473 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:42:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Rolling extremes and R multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | `DG482473` representative; partner #482797 (DUPLICATE), Jaccard 0.859. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 40] x `rr` [5, 2]: **4 trials**; defaults 20 / 5 (the source's); stop look-back 10 fixed.

## Ambiguities resolved

- `tradeCount` is re-declared 0 on every bar (not a `var`), so the 5-trades-a-day cap never binds: dropped.
- Bracket fractions of the signal close, re-based on the fill; risk <= 0 emits no entry.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
