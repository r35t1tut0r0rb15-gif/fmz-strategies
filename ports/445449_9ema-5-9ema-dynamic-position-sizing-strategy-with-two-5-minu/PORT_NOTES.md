# #445449 基于9EMA动态仓位的5分钟双收盘价强势突破策略9EMA-Dynamic-Position-Sizing-Strategy-with-Two-5-Minute-Close-Breakouts -> `fmz_445449_two_strong_closes_above_ema9_long`

- FMZ source id: 445449 (lineage).
- Source: https://www.fmz.com/strategy/445449 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-19 15:03:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Strong closes above the EMA, EMA exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1000 / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [9, 20] x `near_high` [0.99, 0.98]: **4 trials**.

## Ambiguities resolved

- Time window unused; daily bars per the header. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
