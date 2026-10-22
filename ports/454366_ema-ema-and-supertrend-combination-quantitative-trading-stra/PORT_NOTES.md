# #454366 EMA与超级趋势相结合的量化交易策略-EMA-and-Supertrend-Combination-Quantitative-Trading-Strategy -> `fmz_454366_close_ema20_cross_classic_supertrend_long`

- FMZ source id: 454366 (lineage).
- Source: https://www.fmz.com/strategy/454366 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 16:52:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a Supertrend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50] x `atr_len` [10, 14] x `mult` [3.0, 2.0]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
