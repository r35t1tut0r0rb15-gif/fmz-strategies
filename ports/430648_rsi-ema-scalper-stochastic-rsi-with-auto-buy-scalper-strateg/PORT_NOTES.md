# #430648 基于随机-RSI-和-EMA-的自主买入式震荡Scalper策略Stochastic-RSI-with-Auto-Buy-Scalper-Strategy -> `fmz_430648_stochrsi_auto_buy_scalper_long`

- FMZ source id: 430648 (lineage).
- Source: https://www.fmz.com/strategy/430648 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-31 11:34:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | Stochastic-RSI levels, moving averages and percentages. |
| 3 | PASS | "BTCUSD" in the alert texts only; exchange pair in the header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_entry` [17, 25] x `stop_pct` [1.5, 3.0]: **4 trials**; RSI / stochastic 14, K / D 3 and the 1 % profit fixed.

## Ambiguities resolved

- Close-checked exits from the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
