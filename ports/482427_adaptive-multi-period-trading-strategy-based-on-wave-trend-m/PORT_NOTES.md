# #482427 基于波浪趋势动量突破的自适应多周期交易策略-Adaptive-Multi-Period-Trading-Strategy-Based-on-Wave-Trend-Momentum-Breakout -> `fmz_482427_wavetrend_extreme_cross_always_in`

- FMZ source id: 482427 (lineage).
- Source: https://www.fmz.com/strategy/482427 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:52:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | The WaveTrend oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` [60, 53] x `n2` [21, 34]: **4 trials**; defaults 60 / 21 (the source's level 1); channel 10 fixed.

## Ambiguities resolved

- The closes repeat the reversal. REVERSAL INTENDED (always in). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
