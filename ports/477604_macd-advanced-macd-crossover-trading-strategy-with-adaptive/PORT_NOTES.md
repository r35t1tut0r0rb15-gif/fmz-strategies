# #477604 高级MACD均线交叉交易策略结合自适应风险管理-Advanced-MACD-Crossover-Trading-Strategy-with-Adaptive-Risk-Management -> `fmz_477604_macd_cross_swing3_stop_r15_flat_only`

- FMZ source id: 477604 (lineage).
- Source: https://www.fmz.com/strategy/477604 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:34:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar swing bracket as fractions of the fill |
| 2 | PASS | MACD crossings with a swing stop and R target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`velas_sl` [3, 5] x `ratio` [1.5, 2.5]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- Entries only from flat (a loop follows the bracket on the bar's high / low). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`coarse_bar_stop`
