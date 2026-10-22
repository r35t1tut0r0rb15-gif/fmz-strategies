# #454145 基于200日均线和随机振子的趋势追踪策略-Trend-Following-Strategy-Based-on-200-Day-Moving-Average-and-Stochastic-Oscillator -> `fmz_454145_stoch2_turn_vs_ema200_point_bracket_reversal`

- FMZ source id: 454145 (lineage).
- Source: https://www.fmz.com/strategy/454145 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:32:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price-unit levels as fractions of 42000; re-issued levels pending (mark) |
| 2 | PASS | Stochastic turns against the EMA 200 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [2, 5] x `sl_frac` [2.38e-05, 0.01] x `tp_frac` [0.000381, 0.02]: **8 trials**; the EMA 200 and the 20 / 80 levels fixed.

## Ambiguities resolved

- Price units as fractions of 42000; re-issued levels pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
