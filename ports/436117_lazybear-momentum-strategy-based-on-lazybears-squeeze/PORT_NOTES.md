# #436117 基于LazyBear压力矩量化动量策略Momentum-Strategy-Based-on-LazyBears-Squeeze -> `fmz_436117_squeeze_momentum_slope_long`

- FMZ source id: 436117 (lineage).
- Source: https://www.fmz.com/strategy/436117 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-21 14:22:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum regression and a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial balance input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `ema_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- linreg end value; sign of the slope. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
