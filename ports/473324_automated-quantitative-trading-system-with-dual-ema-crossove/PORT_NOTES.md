# #473324 Automated Quantitative Trading System with Dual EMA Crossover and Risk Management -> `fmz_473324_ema21_50_cross_tick_bracket_reversal`

- FMZ source id: 473324 (lineage).
- Source: https://www.fmz.com/strategy/473324 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 11:20:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples from the signal close |
| 2 | PASS | EMA crossings with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.0267, 1.0] x `tp_atr` [0.0533, 2.0]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Ticks as ATR multiples (0.1 tick, hourly ATR ~150). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
