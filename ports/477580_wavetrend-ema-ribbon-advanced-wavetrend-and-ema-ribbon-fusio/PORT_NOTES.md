# #477580 高级WaveTrend与EMA-Ribbon融合交易策略-Advanced-WaveTrend-and-EMA-Ribbon-Fusion-Trading-Strategy -> `fmz_477580_ema_ribbon_wavetrend_swing_stop_r_target_reversal`

- FMZ source id: 477580 (lineage).
- Source: https://www.fmz.com/strategy/477580 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 15:21:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | EMA-ribbon / WaveTrend signals with swing stops and R targets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 and capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_rr` [2.0, 1.5] x `short_rr` [3.0, 2.0]: **4 trials**; the WaveTrend and ribbon lengths fixed.

## Ambiguities resolved

- Repeat-signal re-sends not followed. A both-sided bar goes short. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
