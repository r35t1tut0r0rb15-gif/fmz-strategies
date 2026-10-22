# #488010 Multi EMA Crossover Momentum Alert Trading Strategy -> `fmz_488010_ema10_20_50_trend_ema5_momentum_ema15_exit_cooldown_flat`

- FMZ source id: 488010 (lineage).
- Source: https://www.fmz.com/strategy/488010 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 13:49:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend states with an EMA exit and a momentum warning close |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Strategy(): capital 500, commission 0.1 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len15` [15, 20] x `cooldownBars` [2, 5]: **4 trials**; EMA 5 / 10 / 20 / 50, warning 2.5.

## Ambiguities resolved

- The state, cooldown and warning loop are as written. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
