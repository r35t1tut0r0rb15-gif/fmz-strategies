# #458232 动量驱动型均线-RSI交叉策略-Momentum-Driven-EMA-RSI-Crossover-Strategy -> `fmz_458232_close_cross_ema450_rsi67_exit_rsi80_long`

- FMZ source id: 458232 (lineage).
- Source: https://www.fmz.com/strategy/458232 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 10:31:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Long-EMA crossings with RSI momentum |
| 3 | PASS | Exchange pair in the header only (RNDRUSDT named in a comment). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [450, 200] x `buy_th` [67, 60] x `sell_th` [80, 75]: **8 trials**.

## Ambiguities resolved

- Header's 1-minute bars followed (the title says 5 minutes). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
