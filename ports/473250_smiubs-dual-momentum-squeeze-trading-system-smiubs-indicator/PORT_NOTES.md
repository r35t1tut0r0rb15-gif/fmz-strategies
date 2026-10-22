# #473250 双重动量挤压交易系统SMIUBS指标组合策略-Dual-Momentum-Squeeze-Trading-System-SMIUBS-Indicator-Combination-Strategy -> `fmz_473250_squeeze_momentum_down_sma14_cross_short`

- FMZ source id: 473250 (lineage).
- Source: https://www.fmz.com/strategy/473250 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:52:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | Momentum-down shorts below an SMA with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.004, 0.02] x `sl_pct` [0.025, 0.01]: **4 trials**; the momentum lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar. Short only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
