# #439859 利用EMA指标进行跟踪的趋势策略EMA-Tracking-Strategy -> `fmz_439859_ema50_band_break_long`

- FMZ source id: 439859 (lineage).
- Source: https://www.fmz.com/strategy/439859 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-24 14:27:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA band sides |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [50, 20] x `percent` [0.003, 0.01]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
