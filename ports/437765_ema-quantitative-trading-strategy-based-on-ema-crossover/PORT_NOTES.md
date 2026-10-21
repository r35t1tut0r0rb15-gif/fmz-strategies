# #437765 基于EMA均线交叉的短期量化交易策略Quantitative-Trading-Strategy-Based-on-EMA-Crossover -> `fmz_437765_ema_cross_tick_bracket`

- FMZ source id: 437765 (lineage).
- Source: https://www.fmz.com/strategy/437765 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 14:01:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.0007, 0.5] x `fast` [9, 5]: **4 trials**; EMA 15 / 50 and the 2:1 target fixed.

## Ambiguities resolved

- One-tick bracket -> ATR multiples (reading and a wider stop). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
