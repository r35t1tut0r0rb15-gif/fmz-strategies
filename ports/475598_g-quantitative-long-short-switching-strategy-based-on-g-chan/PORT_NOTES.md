# #475598 基于G通道和指数移动平均的量化多空转换策略-Quantitative-Long-Short-Switching-Strategy-Based-on-G-Channel-and-EMA -> `fmz_475598_g_channel100_ema50_state_long`

- FMZ source id: 475598 (lineage).
- Source: https://www.fmz.com/strategy/475598 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:31:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | G-Channel state against an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `ema_length` [50, 100]: **4 trials**.

## Ambiguities resolved

- nz seeds of 0; cross tests as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
