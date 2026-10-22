# #489154 Multi EMA Crossover Momentum Strategy with Risk Reward Optimization -> `fmz_489154_ema50_200_cross_sl1_tp2pct_reversal`

- FMZ source id: 489154 (lineage).
- Source: https://www.fmz.com/strategy/489154 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 11:19:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a percent bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stopLossPercent` [1.0, 2.0] x `riskRewardRatio` [2.0, 3.0]: **4 trials**; EMA 50 / 200.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
