# #443043 基于双EMA策略分析The-Double-EMA-Strategy-Analysis -> `fmz_443043_ema9_21_cross_reversal_daily`

- FMZ source id: 443043 (lineage).
- Source: https://www.fmz.com/strategy/443043 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-28 18:07:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
