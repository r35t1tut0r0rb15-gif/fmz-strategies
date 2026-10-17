# #482906 复合趋势均线反转交易策略-Composite-Trend-Moving-Average-Reversal-Trading-Strategy -> `fmz_482906_composite_ema_reaction_reversal_1d`

- FMZ source id: 482906 (lineage).
- Source: https://www.fmz.com/strategy/482906 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:23:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving average and a percentage band. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`comp_period` [25, 50] x `reaction_pct` [0.5, 1.0]: **4 trials**; defaults 25 / 0.5 (the source's composite of
20 / 30, EMA).

## Ambiguities resolved

- The composite period is the rounded average of 20 and 30; MA type EMA by default.
- close + entry is a reversal: only entries emitted. REVERSAL INTENDED; no exits or stops.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
