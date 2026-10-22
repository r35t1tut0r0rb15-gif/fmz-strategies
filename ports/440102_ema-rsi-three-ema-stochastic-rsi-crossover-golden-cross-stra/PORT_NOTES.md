# #440102 三重EMA随机RSI交叉金叉策略Three-EMA-Stochastic-RSI-Crossover-Golden-Cross-Strategy -> `fmz_440102_stoch_rsi_cross_three_ema_atr_bracket`

- FMZ source id: 440102 (lineage).
- Source: https://www.fmz.com/strategy/440102 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 16:07:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | Stochastic RSI, EMA alignment, ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_factor` [3.0, 1.5] x `profit_factor` [2.0, 4.0]: **4 trials**; the oscillator and EMA lengths fixed.

## Ambiguities resolved

- ATR from the signal bar (fill-bar ATR in the script). Entries only from flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
